from pathlib import Path

import pytest

from a2a_mail_notify.config import load_settings
from a2a_mail_notify.models import EmailAlert, NotifyResult
from a2a_mail_notify.services.mailbox import MailboxService
from a2a_mail_notify.services.whatsapp import WhatsAppService
from a2a_mail_notify.storage.state_db import StateDB


class FakeOllama:
    async def extract_email_fields(self, sender: str, subject: str, body: str) -> dict[str, str]:
        return {"sender": sender, "subject": subject}

    async def format_whatsapp_alert(self, sender, subject, priority, snippet) -> str:
        flag = "TOP PRIORITY\n" if priority else ""
        return f"{flag}From: {sender}\nSubject: {subject}"


class FakeEmailMcp:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    async def call_tool(self, name: str, arguments: dict | None = None):
        arguments = arguments or {}
        self.calls.append((name, arguments))
        if name == "list_unread":
            return {
                "count": 2,
                "messages": [
                    {
                        "uid": "1",
                        "message_id": "<one@x>",
                        "sender": "Ada <ada@x.com>",
                        "subject": "Job opening",
                    },
                    {
                        "uid": "2",
                        "message_id": "<two@x>",
                        "sender": "Bob <bob@x.com>",
                        "subject": "Lunch",
                    },
                ],
            }
        if name == "fetch_message":
            uid = arguments["uid"]
            if uid == "1":
                return {
                    "uid": "1",
                    "message_id": "<one@x>",
                    "sender": "Ada <ada@x.com>",
                    "subject": "Job opening",
                    "body": "We have an opportunity for you.",
                }
            return {
                "uid": "2",
                "message_id": "<two@x>",
                "sender": "Bob <bob@x.com>",
                "subject": "Lunch",
                "body": "Are you free Friday?",
            }
        if name == "mark_seen":
            return {"ok": True, "uid": arguments["uid"]}
        raise AssertionError(name)


class FakeWhatsAppMcp:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def call_tool(self, name: str, arguments: dict | None = None):
        assert name == "send_notification"
        self.calls.append(arguments or {})
        return {"ok": True, "provider": "meta", "dry_run": True, "body": arguments.get("body", "")}


@pytest.mark.asyncio
async def test_mailbox_service_flags_priority_and_notifies(tmp_config, tmp_path: Path):
    settings = load_settings()
    state = StateDB(tmp_path / "state.db")
    await state.initialize()
    email_mcp = FakeEmailMcp()
    alerts: list[EmailAlert] = []

    async def notify(alert: EmailAlert) -> None:
        alerts.append(alert)

    service = MailboxService(settings, FakeOllama(), state, email_mcp, notify)
    stats = await service.check_mailbox()
    assert stats.listed == 2
    assert stats.notified == 2
    assert stats.errors == 0
    assert alerts[0].priority is True
    assert alerts[1].priority is False
    assert await state.is_processed("<one@x>")

    stats2 = await service.check_mailbox()
    assert stats2.skipped_processed == 2
    assert stats2.notified == 0


@pytest.mark.asyncio
async def test_whatsapp_service_sends_priority_body(tmp_config):
    settings = load_settings()
    mcp = FakeWhatsAppMcp()
    service = WhatsAppService(settings, FakeOllama(), mcp)
    result = await service.notify(
        EmailAlert(sender="Ada", subject="Job opening", priority=True, snippet="hi")
    )
    assert result.ok is True
    assert "TOP PRIORITY" in mcp.calls[0]["body"]
    assert mcp.calls[0]["sender"] == "Ada"
