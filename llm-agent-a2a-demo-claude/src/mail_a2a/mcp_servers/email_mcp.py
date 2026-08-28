"""MCP server: mailbox tools used by the mailbox agent (agent 1).

Runs over stdio as a subprocess of the mailbox agent. Every tool invocation is
logged to the shared log file (and to stderr — stdout is the MCP transport).
"""

from __future__ import annotations

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
from mail_a2a.providers.mailbox import Mailbox, build_mailbox

log = get_logger(__name__)
SERVER_NAME = "email-mcp"

mcp = MCPServer(
    SERVER_NAME,
    instructions="Read-only mailbox access: list messages with sender, subject and body snippet.",
)


def _mailbox() -> Mailbox:
    return build_mailbox(get_settings().mailbox)


def _log_call(tool: str, **kwargs: Any) -> None:
    log.info("mcp_tool_invoked", server=SERVER_NAME, tool=tool, args=redact(kwargs))


@mcp.tool()
def ping() -> dict:
    """Check that the configured mailbox is reachable and report its message count."""
    _log_call("ping")
    mailbox = _mailbox()
    try:
        result = mailbox.ping()
    finally:
        mailbox.close()
    log.info("mcp_tool_done", server=SERVER_NAME, tool="ping", ok=result.get("ok"))
    return result


@mcp.tool()
def list_messages(max_results: int = 10, unread_only: bool = True) -> dict:
    """List recent mailbox messages, newest first, with sender, subject and a body snippet.

    Args:
        max_results: Maximum number of messages to return.
        unread_only: When true, only unread messages are returned.
    """
    _log_call("list_messages", max_results=max_results, unread_only=unread_only)
    mailbox = _mailbox()
    try:
        messages = mailbox.list_messages(max_results=max_results, unread_only=unread_only)
    finally:
        mailbox.close()
    log.info("mcp_tool_done", server=SERVER_NAME, tool="list_messages", count=len(messages))
    return {"count": len(messages), "messages": [item.model_dump() for item in messages]}


@mcp.tool()
def mark_seen(uid: str) -> dict:
    """Mark a message as read by its UID (no-op unless mailbox.mark_seen is enabled).

    Args:
        uid: The mailbox UID of the message.
    """
    _log_call("mark_seen", uid=uid)
    mailbox = _mailbox()
    try:
        ok = mailbox.mark_seen(uid)
    finally:
        mailbox.close()
    log.info("mcp_tool_done", server=SERVER_NAME, tool="mark_seen", uid=uid, ok=ok)
    return {"ok": ok, "uid": uid}


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
        mailbox_provider=settings.mailbox.provider,
        pid=os.getpid(),
    )
    mcp.run()


if __name__ == "__main__":
    main()
