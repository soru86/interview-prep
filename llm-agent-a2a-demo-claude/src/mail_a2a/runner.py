"""Entry point: boots both A2A agents and drives the mailbox scan.

    python -m mail_a2a.runner              # one scan, then exit
    python -m mail_a2a.runner --watch      # scan every poll_interval_seconds
    python -m mail_a2a.runner --check      # health checks only
    python -m mail_a2a.runner --serve      # keep the agents up, drive them yourself

The two agents run as separate uvicorn servers in this process. They only ever
talk to each other over HTTP JSON-RPC, so splitting them across machines is a
config change, not a code change.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import os
import sys
from pathlib import Path

import httpx
import uvicorn

from mail_a2a.a2a_common import open_a2a_client, send_json
from mail_a2a.agents.mailbox_agent import build_mailbox_app
from mail_a2a.agents.whatsapp_agent import build_whatsapp_app
from mail_a2a.config import (
    CONFIG_PATH_ENV,
    ConfigError,
    Settings,
    clear_settings_cache,
    config_path,
    get_settings,
)
from mail_a2a.llm import OllamaClient
from mail_a2a.logging_setup import configure_logging, get_logger
from mail_a2a.mcp_client import open_email_mcp, open_whatsapp_mcp
from mail_a2a.models import ScanRequest, ScanResult

log = get_logger(__name__)

AGENT_CARD_PATH = "/.well-known/agent-card.json"


async def _serve(app, host: str, port: int, name: str) -> uvicorn.Server:
    config = uvicorn.Config(app, host=host, port=port, log_config=None, access_log=False)
    server = uvicorn.Server(config)
    asyncio.get_running_loop().create_task(server.serve(), name=f"uvicorn-{name}")
    return server


async def _await_card(url: str, name: str, timeout: float = 20.0) -> None:
    """Block until the agent's card is being served."""
    deadline = asyncio.get_running_loop().time() + timeout
    async with httpx.AsyncClient(timeout=3) as client:
        while asyncio.get_running_loop().time() < deadline:
            try:
                response = await client.get(f"{url}{AGENT_CARD_PATH}")
                if response.status_code == 200:
                    log.info("agent_online", agent=name, url=url)
                    return
            except Exception:
                pass
            await asyncio.sleep(0.25)
    raise RuntimeError(f"{name} did not come up at {url} within {timeout:.0f}s")


@contextlib.asynccontextmanager
async def running_agents(settings: Settings):
    """Start both A2A servers, yield once their cards resolve, shut down after."""
    mailbox_endpoint = settings.agents.mailbox
    whatsapp_endpoint = settings.agents.whatsapp

    whatsapp_server = await _serve(
        build_whatsapp_app(settings), whatsapp_endpoint.host, whatsapp_endpoint.port, "whatsapp"
    )
    mailbox_server = await _serve(
        build_mailbox_app(settings), mailbox_endpoint.host, mailbox_endpoint.port, "mailbox"
    )
    try:
        await _await_card(whatsapp_endpoint.url, "whatsapp-notifier-agent")
        await _await_card(mailbox_endpoint.url, "mailbox-reader-agent")
        yield
    finally:
        log.info("agents_shutting_down")
        for server in (mailbox_server, whatsapp_server):
            server.should_exit = True
        await asyncio.sleep(0.3)


async def run_scan(settings: Settings) -> ScanResult:
    """Ask the mailbox agent, over A2A, to scan and notify."""
    peer_url = settings.agents.mailbox.url
    request = ScanRequest(max_emails=settings.max_emails, unread_only=settings.mailbox.unread_only)
    # A full scan runs one LLM call per email in each agent, so allow plenty of time.
    timeout = settings.ollama.timeout_seconds * 2 * max(settings.max_emails, 1) + 60

    async with open_a2a_client(peer_url, timeout_seconds=timeout) as client:
        reply = await send_json(
            client, request.model_dump(), peer=peer_url, skill="scan_and_notify"
        )
    return ScanResult.model_validate(reply) if reply else ScanResult(error="empty A2A reply")


def _report(result: ScanResult) -> None:
    log.info(
        "scan_result",
        scanned=result.scanned,
        new=result.new,
        notified=result.notified,
        failed=result.failed,
        top_priority=result.priority,
        error=result.error or None,
    )
    for item in result.results:
        log.info(
            "notification",
            uid=item.uid,
            ok=item.ok,
            provider=item.provider,
            to=item.to,
            message_id=item.message_id or None,
            error=item.error or None,
        )


async def run_checks(settings: Settings) -> bool:
    """Verify Ollama, the mailbox MCP server and the WhatsApp MCP server."""
    ok = True

    health = await OllamaClient(settings.ollama, agent="runner").health()
    if not health.get("ok"):
        log.error("check_ollama_unreachable", base_url=settings.ollama.base_url)
        ok = False
    elif not health.get("model_present"):
        log.error(
            "check_model_missing",
            model=settings.ollama.model,
            hint="docker compose up -d  (the ollama-pull sidecar pulls the model)",
        )
        ok = False
    else:
        log.info("check_ollama_ok", model=settings.ollama.model)

    try:
        async with open_email_mcp() as mcp:
            result = await mcp.call("ping")
        log.info("check_mailbox_ok", detail=result)
    except Exception as exc:
        log.error("check_mailbox_failed", error=str(exc))
        ok = False

    try:
        async with open_whatsapp_mcp() as mcp:
            channel = await mcp.call("describe_channel")
            credentials = await mcp.call("verify_credentials")
        if not channel.get("configured"):
            log.error("check_whatsapp_no_recipient", hint="set whatsapp.to in config/config.yaml")
            ok = False
        elif not credentials.get("ok"):
            log.error(
                "check_whatsapp_credentials_rejected",
                provider=channel.get("provider"),
                error=credentials.get("error"),
            )
            ok = False
        else:
            log.info("check_whatsapp_ok", detail=channel | credentials)
    except Exception as exc:
        log.error("check_whatsapp_failed", error=str(exc))
        ok = False

    log.info("checks_complete", ok=ok)
    return ok


async def main_async(args: argparse.Namespace) -> int:
    if args.config:
        os.environ[CONFIG_PATH_ENV] = str(Path(args.config).resolve())
    clear_settings_cache()

    target = config_path()
    settings = get_settings()
    configure_logging(level=settings.logging.level, log_file=settings.logging.file)

    if not target.is_file():
        log.warning(
            "config_missing",
            path=str(target),
            hint="cp config/config.example.yaml config/config.yaml — using defaults for now",
        )

    log.info(
        "startup",
        config=str(target),
        mailbox_provider=settings.mailbox.provider,
        whatsapp_provider=settings.whatsapp.provider,
        whatsapp_to=settings.whatsapp.to or "(unset)",
        model=settings.ollama.model,
        priority_keywords=settings.priority_keywords,
        log_file=settings.logging.file,
    )

    if args.check:
        return 0 if await run_checks(settings) else 1

    async with running_agents(settings):
        if args.serve:
            log.info(
                "serving",
                mailbox=settings.agents.mailbox.url,
                whatsapp=settings.agents.whatsapp.url,
            )
            with contextlib.suppress(asyncio.CancelledError, KeyboardInterrupt):
                while True:
                    await asyncio.sleep(3600)
            return 0

        if args.watch:
            log.info("watch_mode", interval_seconds=settings.poll_interval_seconds)
            while True:
                _report(await run_scan(settings))
                await asyncio.sleep(settings.poll_interval_seconds)

        result = await run_scan(settings)
        _report(result)
        return 1 if result.error or result.failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mail-a2a",
        description="Two-agent A2A mailbox-to-WhatsApp notifier running on DeepSeek R1 1.5B.",
    )
    parser.add_argument("--config", help="path to config.yaml (default: config/config.yaml)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--watch", action="store_true", help="scan repeatedly on the poll interval")
    mode.add_argument("--serve", action="store_true", help="run the agents without scanning")
    mode.add_argument("--check", action="store_true", help="health-check the dependencies and exit")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        sys.exit(asyncio.run(main_async(args)))
    except ConfigError as exc:
        # Logging may not be configured yet, and a parser traceback helps nobody.
        print(f"\nConfiguration error:\n{exc}\n", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        log.info("interrupted")
        sys.exit(130)


if __name__ == "__main__":
    main()
