from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any

from mcp.server import MCPServer

from a2a_mail_notify.config import clear_settings_cache, get_settings
from a2a_mail_notify.logging import configure_mcp_logging, get_logger, mcp_log_file_from_env, sanitize_log_data
from a2a_mail_notify.providers.imap import ImapProvider, build_imap_provider

log = get_logger(__name__)

mcp = MCPServer("email-mcp", instructions="IMAP tools for listing and fetching mailbox messages.")


@contextmanager
def _imap() -> ImapProvider:
    settings = get_settings()
    provider = build_imap_provider(settings, allow_interactive_login=False)
    provider.connect()
    try:
        yield provider
    finally:
        provider.close()


def _log_tool(name: str, **kwargs: Any) -> None:
    log.info("mcp_server_tool", server="email-mcp", tool=name, args=sanitize_log_data(kwargs))


@mcp.tool()
def ping() -> dict:
    """Check IMAP connectivity and selected folder."""
    _log_tool("ping")
    with _imap() as mailbox:
        result = mailbox.ping()
    log.info("mcp_server_tool_done", server="email-mcp", tool="ping", ok=result.get("ok"))
    return result


@mcp.tool()
def list_unread(max_results: int = 20, unread_only: bool = True) -> dict:
    """List recent messages (unread by default) with sender and subject headers."""
    _log_tool("list_unread", max_results=max_results, unread_only=unread_only)
    with _imap() as mailbox:
        summaries = mailbox.list_unread(max_results=max_results, unread_only=unread_only)
    payload = {"messages": [item.model_dump() for item in summaries], "count": len(summaries)}
    log.info("mcp_server_tool_done", server="email-mcp", tool="list_unread", count=len(summaries))
    return payload


@mcp.tool()
def fetch_message(uid: str) -> dict:
    """Fetch a full IMAP message by UID, including plain-text body."""
    _log_tool("fetch_message", uid=uid)
    with _imap() as mailbox:
        message = mailbox.fetch_message(uid)
    log.info("mcp_server_tool_done", server="email-mcp", tool="fetch_message", uid=uid)
    return message.model_dump()


@mcp.tool()
def mark_seen(uid: str) -> dict:
    """Mark an IMAP message as seen by UID."""
    _log_tool("mark_seen", uid=uid)
    with _imap() as mailbox:
        ok = mailbox.mark_seen(uid)
    log.info("mcp_server_tool_done", server="email-mcp", tool="mark_seen", uid=uid, ok=ok)
    return {"ok": ok, "uid": uid}


def main() -> None:
    clear_settings_cache()
    settings = get_settings()
    configure_mcp_logging(
        level=os.environ.get("A2A_LOG_LEVEL", settings.logging.level),
        log_file=mcp_log_file_from_env() or settings.logging.file,
    )
    log.info("mcp_server_start", server="email-mcp", transport="stdio")
    mcp.run()


if __name__ == "__main__":
    main()
