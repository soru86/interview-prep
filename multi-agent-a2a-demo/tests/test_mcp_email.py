import pytest
from mcp import Client

from a2a_mail_notify.mcp_client import tool_result_payload
from a2a_mail_notify.mcp_servers import email_mcp
from a2a_mail_notify.models import EmailMessage, EmailSummary


class FakeImap:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def connect(self) -> None:
        return None

    def close(self) -> None:
        return None

    def ping(self) -> dict:
        return {"ok": True, "host": "imap.example.com", "folder": "INBOX"}

    def list_unread(self, max_results: int = 20, unread_only: bool = True):
        return [
            EmailSummary(
                uid="11",
                message_id="<a@x>",
                sender="Ada <ada@x.com>",
                subject="Job opening",
            )
        ]

    def fetch_message(self, uid: str) -> EmailMessage:
        return EmailMessage(
            uid=uid,
            message_id="<a@x>",
            sender="Ada <ada@x.com>",
            subject="Job opening",
            body="We have a position available.",
        )

    def mark_seen(self, uid: str) -> bool:
        return True


@pytest.mark.asyncio
async def test_email_mcp_tools(tmp_config, monkeypatch):
    monkeypatch.setattr(email_mcp, "build_imap_provider", lambda *args, **kwargs: FakeImap())
    async with Client(email_mcp.mcp, raise_exceptions=True) as client:
        tools = await client.list_tools()
        names = {tool.name for tool in tools.tools}
        assert names == {"ping", "list_unread", "fetch_message", "mark_seen"}

        ping = tool_result_payload(await client.call_tool("ping", {}))
        assert ping["ok"] is True

        listed = tool_result_payload(await client.call_tool("list_unread", {"max_results": 5}))
        assert listed["count"] == 1
        assert listed["messages"][0]["subject"] == "Job opening"

        fetched = tool_result_payload(await client.call_tool("fetch_message", {"uid": "11"}))
        assert "position" in fetched["body"]

        seen = tool_result_payload(await client.call_tool("mark_seen", {"uid": "11"}))
        assert seen["ok"] is True
