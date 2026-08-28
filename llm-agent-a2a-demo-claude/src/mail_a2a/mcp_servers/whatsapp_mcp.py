"""MCP server: WhatsApp tools used by the notifier agent (agent 2).

Runs over stdio as a subprocess of the WhatsApp agent. The destination number
comes from the config file; a tool caller may override it, but the default is
what the brief asks for.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from mcp.server import MCPServer

from mail_a2a.config import clear_settings_cache, get_settings
from mail_a2a.logging_setup import (
    configure_stdio_server_logging,
    get_logger,
    log_file_from_env,
    redact,
)
from mail_a2a.providers.whatsapp import build_channel

log = get_logger(__name__)
SERVER_NAME = "whatsapp-mcp"

mcp = MCPServer(
    SERVER_NAME,
    instructions="Send WhatsApp notifications through the configured provider.",
)


def _log_call(tool: str, **kwargs: Any) -> None:
    log.info("mcp_tool_invoked", server=SERVER_NAME, tool=tool, args=redact(kwargs))


@mcp.tool()
def describe_channel() -> dict:
    """Report which WhatsApp provider is configured and the default destination number."""
    _log_call("describe_channel")
    settings = get_settings()
    return {
        "provider": settings.whatsapp.provider,
        "default_to": settings.whatsapp.to,
        "configured": bool(settings.whatsapp.to),
    }


@mcp.tool()
def verify_credentials() -> dict:
    """Check that the configured WhatsApp provider accepts its credentials."""
    _log_call("verify_credentials")
    settings = get_settings()
    try:
        channel = build_channel(settings.whatsapp)
    except RuntimeError as exc:
        return {"ok": False, "provider": settings.whatsapp.provider, "error": str(exc)}
    result = asyncio.run(channel.verify())
    log.info(
        "mcp_tool_done",
        server=SERVER_NAME,
        tool="verify_credentials",
        ok=result.get("ok"),
    )
    return result


@mcp.tool()
def send_whatsapp_message(text: str, to: str = "", priority: bool = False) -> dict:
    """Send a WhatsApp message to the configured recipient.

    Args:
        text: The message body to deliver.
        to: Destination number in international format; defaults to whatsapp.to from config.
        priority: Marks the notification as top priority (used for logging and formatting).
    """
    settings = get_settings()
    destination = to or settings.whatsapp.to
    _log_call("send_whatsapp_message", to=destination, priority=priority, chars=len(text))

    if not destination:
        log.error("mcp_tool_error", server=SERVER_NAME, tool="send_whatsapp_message",
                  error="no destination configured")
        return {"ok": False, "error": "whatsapp.to is not set in the config file"}

    channel = build_channel(settings.whatsapp)
    # MCPServer runs sync tools in a worker thread, so there is no running loop here.
    result = asyncio.run(channel.send(destination, text, priority=priority))
    log.info(
        "mcp_tool_done",
        server=SERVER_NAME,
        tool="send_whatsapp_message",
        ok=result.get("ok"),
        provider=result.get("provider"),
    )
    return result


def main() -> None:
    clear_settings_cache()
    settings = get_settings()
    configure_stdio_server_logging(
        level=os.environ.get("MAIL_A2A_LOG_LEVEL", settings.logging.level),
        log_file=log_file_from_env() or settings.logging.file,
    )
    log.info(
        "mcp_server_start",
        server=SERVER_NAME,
        transport="stdio",
        provider=settings.whatsapp.provider,
        pid=os.getpid(),
    )
    mcp.run()


if __name__ == "__main__":
    main()
