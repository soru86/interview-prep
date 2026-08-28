from __future__ import annotations

import os
from typing import Any

from mcp.server import MCPServer

from a2a_mail_notify.config import clear_settings_cache, get_settings
from a2a_mail_notify.logging import configure_mcp_logging, get_logger, mcp_log_file_from_env, sanitize_log_data
from a2a_mail_notify.providers.whatsapp import build_alert_body, build_notifier

log = get_logger(__name__)

mcp = MCPServer("whatsapp-mcp", instructions="Send WhatsApp email-alert notifications.")


def _log_tool(name: str, **kwargs: Any) -> None:
    log.info("mcp_server_tool", server="whatsapp-mcp", tool=name, args=sanitize_log_data(kwargs))


@mcp.tool()
async def send_notification(
    sender: str,
    subject: str,
    priority: bool = False,
    body: str = "",
    snippet: str = "",
) -> dict:
    """Send a WhatsApp notification about an email (Meta or Twilio, from config)."""
    settings = get_settings()
    message_body = body or build_alert_body(sender, subject, priority, snippet)
    _log_tool(
        "send_notification",
        sender=sender,
        subject=subject,
        priority=priority,
        to=settings.whatsapp.to,
        provider=settings.whatsapp.provider,
        dry_run=settings.dry_run,
    )
    notifier = build_notifier(settings)
    result = await notifier.send_notification(
        sender=sender,
        subject=subject,
        priority=priority,
        body=message_body,
    )
    log.info(
        "mcp_server_tool_done",
        server="whatsapp-mcp",
        tool="send_notification",
        ok=result.ok,
        dry_run=result.dry_run,
        provider=result.provider,
        message_id=result.message_id,
    )
    return result.model_dump()


def main() -> None:
    clear_settings_cache()
    settings = get_settings()
    configure_mcp_logging(
        level=os.environ.get("A2A_LOG_LEVEL", settings.logging.level),
        log_file=mcp_log_file_from_env() or settings.logging.file,
    )
    log.info("mcp_server_start", server="whatsapp-mcp", transport="stdio")
    mcp.run()


if __name__ == "__main__":
    main()
