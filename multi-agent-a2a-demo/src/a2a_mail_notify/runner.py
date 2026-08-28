from __future__ import annotations

import argparse
import asyncio
import json
import socket
import sys

import httpx
import uvicorn
from a2a.client import A2ACardResolver, ClientConfig, create_client

from a2a_mail_notify.a2a_support import send_a2a_text
from a2a_mail_notify.agents.mailbox import create_mailbox_app
from a2a_mail_notify.agents.whatsapp import create_whatsapp_app
from a2a_mail_notify.config import get_settings, load_settings
from a2a_mail_notify.llm.ollama import OllamaClient
from a2a_mail_notify.logging import configure_logging, get_logger
from a2a_mail_notify.providers.imap import build_imap_provider, format_imap_error
from a2a_mail_notify.providers.microsoft_oauth import MicrosoftImapAuth
from a2a_mail_notify.storage.state_db import StateDB


def strip_inline_comment_args(argv: list[str] | None = None) -> list[str]:
    """Drop zsh-passthrough tokens starting at '#' (interactive zsh is not comment-aware)."""
    args = list(sys.argv[1:] if argv is None else argv)
    cleaned: list[str] = []
    for arg in args:
        if arg.startswith("#"):
            break
        cleaned.append(arg)
    return cleaned


def mailbox_setup_error(settings) -> str | None:
    mailbox = settings.mailbox
    if not mailbox.username:
        return f"Set mailbox.username in {settings.config_path}"
    if mailbox.auth == "oauth2":
        if not mailbox.oauth_client_id:
            return (
                "Outlook IMAP needs Microsoft OAuth. Set mailbox.oauth_client_id "
                f"in {settings.config_path}, then run: a2a-mail-notify login"
            )
        if not mailbox.oauth_token_cache.exists():
            return "Authorize Outlook IMAP with: a2a-mail-notify login"
        return None
    if not mailbox.password or mailbox.password == "your-app-password":
        return f"Set mailbox.username / mailbox.password in {settings.config_path}"
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the A2A mailbox → WhatsApp multi-agent demo."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser(
        "run",
        help="Start both A2A agents and poll the mailbox (default every 5 seconds)",
    )
    run_parser.add_argument(
        "--once",
        action="store_true",
        help="Check the mailbox once and exit instead of polling",
    )
    run_parser.add_argument("--max-emails", type=int, default=None, help="Max emails per check")
    sub.add_parser("status", help="Show config, Ollama, IMAP, and agent-card health")
    sub.add_parser("login", help="Sign in to Outlook.com IMAP via Microsoft device-code OAuth")
    return parser


def port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex((host, port)) == 0


def port_busy_message(name: str, host: str, port: int) -> str:
    return (
        f"{name} port {host}:{port} is already in use. "
        "A previous a2a-mail-notify run is still listening "
        "(often after Ctrl+Z). Stop it with Ctrl+C, or: "
        f"lsof -nP -iTCP:{port} -sTCP:LISTEN"
    )


async def _serve(app, host: str, port: int, name: str) -> uvicorn.Server:
    if port_in_use(host, port):
        raise RuntimeError(port_busy_message(name, host, port))
    config = uvicorn.Config(app, host=host, port=port, log_level="info", access_log=True)
    server = uvicorn.Server(config)
    serve_task = asyncio.create_task(server.serve())
    deadline = asyncio.get_event_loop().time() + 15
    while asyncio.get_event_loop().time() < deadline:
        if serve_task.done():
            exc = serve_task.exception()
            if exc:
                raise RuntimeError(f"{name} failed to start on {host}:{port}: {exc}") from exc
            raise RuntimeError(port_busy_message(name, host, port))
        if server.started:
            return server
        await asyncio.sleep(0.1)
    raise RuntimeError(f"A2A server at {host}:{port} failed to start")


async def _wait_for_card(url: str, timeout: float = 20.0) -> None:
    async with httpx.AsyncClient(timeout=5) as http:
        resolver = A2ACardResolver(httpx_client=http, base_url=url)
        deadline = asyncio.get_event_loop().time() + timeout
        last_error = None
        while asyncio.get_event_loop().time() < deadline:
            try:
                card = await resolver.get_agent_card()
                log = get_logger("runner")
                log.info("a2a_agent_ready", url=url, name=getattr(card, "name", ""))
                return
            except Exception as exc:
                last_error = exc
                await asyncio.sleep(0.3)
    raise RuntimeError(f"Agent card not reachable at {url}: {last_error}")


async def _trigger_mailbox(max_emails: int | None) -> str:
    settings = get_settings()
    url = settings.agents.mailbox.url
    payload = {"max_emails": max_emails} if max_emails else {"action": "check_mailbox"}
    async with httpx.AsyncClient(timeout=settings.ollama.timeout_seconds + 30) as http:
        resolver = A2ACardResolver(httpx_client=http, base_url=url)
        card = await resolver.get_agent_card()
        client = await create_client(agent=card, client_config=ClientConfig(streaming=False))
        try:
            return await send_a2a_text(
                client,
                json.dumps(payload),
                peer_url=url,
                skill="check_mailbox",
            )
        finally:
            await client.close()


async def run_command(once: bool, max_emails: int | None) -> int:
    settings = get_settings()
    log = get_logger("runner")
    setup_error = mailbox_setup_error(settings)
    if setup_error:
        log.error("mailbox_not_configured", hint=setup_error)
        print(setup_error, file=sys.stderr)
        return 1
    watch = not once
    log.info(
        "runner_start",
        mailbox_url=settings.agents.mailbox.url,
        whatsapp_url=settings.agents.whatsapp.url,
        model=settings.ollama.model,
        dry_run=settings.dry_run,
        watch=watch,
        poll_interval_seconds=settings.poll_interval_seconds,
    )

    wa_server = None
    mb_server = None
    try:
        wa_server = await _serve(
            create_whatsapp_app(settings),
            settings.agents.whatsapp.host,
            settings.agents.whatsapp.port,
            "WhatsApp agent",
        )
        mb_server = await _serve(
            create_mailbox_app(settings),
            settings.agents.mailbox.host,
            settings.agents.mailbox.port,
            "Mailbox agent",
        )
    except RuntimeError as exc:
        log.error("agent_bind_failed", error=str(exc))
        print(exc, file=sys.stderr)
        if wa_server:
            wa_server.should_exit = True
        if mb_server:
            mb_server.should_exit = True
        return 1
    await _wait_for_card(settings.agents.whatsapp.url)
    await _wait_for_card(settings.agents.mailbox.url)
    log.info("agents_listening")

    try:
        while True:
            result = await _trigger_mailbox(max_emails)
            print(result)
            if not watch:
                break
            log.info("watch_sleep", seconds=settings.poll_interval_seconds)
            await asyncio.sleep(settings.poll_interval_seconds)
    finally:
        wa_server.should_exit = True
        mb_server.should_exit = True
        log.info("runner_stop")
    return 0


async def status_command() -> int:
    settings = load_settings()
    config_exists = settings.config_path.exists()
    setup_error = mailbox_setup_error(settings)
    status: dict = {
        "config_path": str(settings.config_path),
        "config_exists": config_exists,
        "next_step": None,
        "mailbox_host": settings.mailbox.host,
        "mailbox_username": settings.mailbox.username,
        "mailbox_auth": settings.mailbox.auth,
        "whatsapp_provider": settings.whatsapp.provider,
        "whatsapp_to": settings.whatsapp.to,
        "ollama_model": settings.ollama.model,
        "dry_run": settings.dry_run,
        "mailbox_agent": settings.agents.mailbox.url,
        "whatsapp_agent": settings.agents.whatsapp.url,
    }
    if not config_exists:
        status["next_step"] = (
            f"Copy the example config: cp config/config.example.yaml {settings.config_path}"
        )
    elif setup_error:
        status["next_step"] = setup_error

    ollama = OllamaClient(
        settings.ollama.base_url,
        settings.ollama.model,
        settings.ollama.timeout_seconds,
    )
    try:
        status["ollama"] = await ollama.health()
    except Exception as exc:
        status["ollama"] = {"ok": False, "error": str(exc)}

    imap = build_imap_provider(settings, allow_interactive_login=False)
    try:
        if setup_error:
            status["imap"] = {"ok": False, "error": setup_error}
        else:
            await asyncio.to_thread(imap.connect)
            status["imap"] = await asyncio.to_thread(imap.ping)
            await asyncio.to_thread(imap.close)
    except Exception as exc:
        status["imap"] = {
            "ok": False,
            "error": format_imap_error(exc, host=settings.mailbox.host, auth=settings.mailbox.auth),
        }

    state = StateDB(settings.state_db_path)
    try:
        await state.initialize()
        status["processed_emails"] = await state.count_processed()
    except Exception as exc:
        status["processed_emails"] = None
        status["state_db_error"] = str(exc)

    async with httpx.AsyncClient(timeout=3) as http:
        for key, url in (
            ("mailbox_agent_card", settings.agents.mailbox.url),
            ("whatsapp_agent_card", settings.agents.whatsapp.url),
        ):
            try:
                resolver = A2ACardResolver(httpx_client=http, base_url=url)
                card = await resolver.get_agent_card()
                status[key] = {"ok": True, "name": getattr(card, "name", "")}
            except Exception:
                status[key] = {
                    "ok": False,
                    "error": "agent not running",
                    "hint": "Start agents with: a2a-mail-notify run",
                }

    print(json.dumps(status, indent=2, default=str))
    return 0


def login_command() -> int:
    settings = load_settings()
    mailbox = settings.mailbox
    if mailbox.auth != "oauth2":
        print(
            "mailbox.auth is not oauth2. Set mailbox.auth: oauth2 in config.yaml for Outlook.com.",
            file=sys.stderr,
        )
        return 1
    if not mailbox.username:
        print(f"Set mailbox.username in {settings.config_path}", file=sys.stderr)
        return 1
    auth = MicrosoftImapAuth(
        client_id=mailbox.oauth_client_id,
        tenant=mailbox.oauth_tenant,
        username=mailbox.username,
        cache_path=mailbox.oauth_token_cache,
    )
    try:
        auth.acquire_device_code()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Outlook IMAP login saved. Next: a2a-mail-notify status")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args(strip_inline_comment_args())
    settings = get_settings()
    configure_logging(settings.logging.level, settings.logging.file)

    if args.command == "run":
        raise SystemExit(asyncio.run(run_command(once=args.once, max_emails=args.max_emails)))
    if args.command == "status":
        raise SystemExit(asyncio.run(status_command()))
    if args.command == "login":
        raise SystemExit(login_command())
    raise SystemExit(1)


if __name__ == "__main__":
    main()
