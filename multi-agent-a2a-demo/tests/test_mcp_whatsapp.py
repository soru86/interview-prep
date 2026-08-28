import pytest
from mcp import Client

from a2a_mail_notify.config import load_settings
from a2a_mail_notify.mcp_client import tool_result_payload
from a2a_mail_notify.mcp_servers import whatsapp_mcp


@pytest.mark.asyncio
async def test_whatsapp_mcp_dry_run(tmp_config):
    settings = load_settings()
    assert settings.dry_run is True
    async with Client(whatsapp_mcp.mcp, raise_exceptions=True) as client:
        tools = await client.list_tools()
        assert {tool.name for tool in tools.tools} == {"send_notification"}
        result = await client.call_tool(
            "send_notification",
            {
                "sender": "Ada <ada@x.com>",
                "subject": "Job opening",
                "priority": True,
                "snippet": "Come join us",
            },
        )
        data = tool_result_payload(result)
        assert data["ok"] is True
        assert data["dry_run"] is True
        assert "TOP PRIORITY" in data["body"]
        assert "Job opening" in data["body"]
