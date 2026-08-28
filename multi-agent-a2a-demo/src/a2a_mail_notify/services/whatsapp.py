from __future__ import annotations

from a2a_mail_notify.config import Settings
from a2a_mail_notify.llm.ollama import OllamaClient
from a2a_mail_notify.logging import get_logger
from a2a_mail_notify.mcp_client import LoggingMcpClient
from a2a_mail_notify.models import EmailAlert, NotifyResult
from a2a_mail_notify.providers.whatsapp import build_alert_body

log = get_logger(__name__)


class WhatsAppService:
    def __init__(
        self,
        settings: Settings,
        ollama: OllamaClient,
        whatsapp_mcp: LoggingMcpClient,
    ) -> None:
        self.settings = settings
        self.ollama = ollama
        self.whatsapp_mcp = whatsapp_mcp

    async def notify(self, alert: EmailAlert) -> NotifyResult:
        body = await self.ollama.format_whatsapp_alert(
            sender=alert.sender,
            subject=alert.subject,
            priority=alert.priority,
            snippet=alert.snippet,
        )
        if alert.priority and "TOP PRIORITY" not in body.upper():
            body = f"TOP PRIORITY\n{body}"
        if not body.strip():
            body = build_alert_body(alert.sender, alert.subject, alert.priority, alert.snippet)

        log.info(
            "whatsapp_notify",
            to=self.settings.whatsapp.to,
            provider=self.settings.whatsapp.provider,
            sender=alert.sender,
            subject=alert.subject,
            priority=alert.priority,
        )
        raw = await self.whatsapp_mcp.call_tool(
            "send_notification",
            {
                "sender": alert.sender,
                "subject": alert.subject,
                "priority": alert.priority,
                "body": body,
                "snippet": alert.snippet,
            },
        )
        if isinstance(raw, dict):
            return NotifyResult.model_validate(raw)
        return NotifyResult(ok=True, body=str(raw), provider=self.settings.whatsapp.provider)
