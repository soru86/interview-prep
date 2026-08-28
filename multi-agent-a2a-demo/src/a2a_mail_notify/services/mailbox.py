from __future__ import annotations

from datetime import datetime, timezone

from a2a_mail_notify.config import Settings
from a2a_mail_notify.llm.ollama import OllamaClient
from a2a_mail_notify.logging import get_logger
from a2a_mail_notify.mcp_client import LoggingMcpClient
from a2a_mail_notify.models import EmailAlert, MailboxRunStats, ProcessedEmailRecord
from a2a_mail_notify.priority import is_top_priority
from a2a_mail_notify.storage.state_db import StateDB

log = get_logger(__name__)


class MailboxService:
    def __init__(
        self,
        settings: Settings,
        ollama: OllamaClient,
        state_db: StateDB,
        email_mcp: LoggingMcpClient,
        notify,
    ) -> None:
        self.settings = settings
        self.ollama = ollama
        self.state_db = state_db
        self.email_mcp = email_mcp
        self.notify = notify

    async def check_mailbox(self, max_emails: int | None = None) -> MailboxRunStats:
        limit = max_emails or self.settings.max_emails
        listed = await self.email_mcp.call_tool(
            "list_unread",
            {
                "max_results": limit,
                "unread_only": self.settings.mailbox.unread_only,
            },
        )
        messages = listed.get("messages", []) if isinstance(listed, dict) else []
        stats = MailboxRunStats(listed=len(messages))
        log.info("mailbox_listed", count=len(messages), unread_only=self.settings.mailbox.unread_only)

        for summary in messages:
            uid = str(summary.get("uid", ""))
            header_id = str(summary.get("message_id") or uid)
            try:
                if await self.state_db.is_processed(header_id):
                    stats.skipped_processed += 1
                    log.info("mailbox_skip_processed", message_id=header_id)
                    continue

                fetched = await self.email_mcp.call_tool("fetch_message", {"uid": uid})
                sender = str(fetched.get("sender") or summary.get("sender") or "")
                subject = str(fetched.get("subject") or summary.get("subject") or "")
                body = str(fetched.get("body") or "")
                message_id = str(fetched.get("message_id") or header_id)

                extracted = await self.ollama.extract_email_fields(sender, subject, body)
                sender = extracted["sender"]
                subject = extracted["subject"]
                priority = is_top_priority(
                    f"{subject}\n{body}",
                    self.settings.priority_keywords,
                )
                alert = EmailAlert(
                    sender=sender,
                    subject=subject,
                    priority=priority,
                    snippet=body[:280],
                    message_id=message_id,
                    uid=uid,
                )
                log.info(
                    "mailbox_alert_ready",
                    sender=sender,
                    subject=subject,
                    priority=priority,
                    message_id=message_id,
                )
                await self.notify(alert)
                await self.state_db.mark_processed(
                    ProcessedEmailRecord(
                        message_id=message_id,
                        status="notified",
                        processed_at=datetime.now(timezone.utc),
                    )
                )
                try:
                    await self.email_mcp.call_tool("mark_seen", {"uid": uid})
                except Exception:
                    log.warning("mailbox_mark_seen_failed", uid=uid)
                stats.notified += 1
                stats.alerts.append(alert)
            except Exception as exc:
                stats.errors += 1
                log.exception("mailbox_email_failed", uid=uid, error=str(exc))
                await self.state_db.mark_processed(
                    ProcessedEmailRecord(
                        message_id=header_id,
                        status="error",
                        processed_at=datetime.now(timezone.utc),
                        error_message=str(exc),
                    )
                )
        return stats
