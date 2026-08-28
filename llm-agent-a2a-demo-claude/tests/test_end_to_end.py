"""Full pipeline over real A2A JSON-RPC and real MCP stdio servers.

Only the LLM is faked — Ollama is not assumed to be running in CI. Everything
else is the production path: two uvicorn servers, agent cards, message/send, and
two MCP subprocesses.
"""

import json
import socket

import pytest
import yaml

from mail_a2a.a2a_common import open_a2a_client, send_json
from mail_a2a.config import load_settings
from mail_a2a.models import ScanResult
from mail_a2a.runner import run_scan, running_agents


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
def settings(tmp_path, monkeypatch):
    """A demo-mailbox, console-WhatsApp config on throwaway ports."""
    config = {
        "mailbox": {"provider": "demo", "sample_file": str(tmp_path / "mail.json")},
        "whatsapp": {"provider": "console", "to": "971568896895"},
        # Unreachable on purpose: the pipeline must not depend on the model.
        "ollama": {"base_url": "http://127.0.0.1:1", "required": False},
        "agents": {
            "mailbox": {"host": "127.0.0.1", "port": _free_port()},
            "whatsapp": {"host": "127.0.0.1", "port": _free_port()},
        },
        "logging": {"level": "WARNING", "file": str(tmp_path / "test.log")},
        "state_file": str(tmp_path / "seen.json"),
        "max_emails": 10,
    }
    (tmp_path / "mail.json").write_text(
        json.dumps(
            {
                "messages": [
                    {
                        "uid": "1",
                        "sender": "Recruiter <talent@example.com>",
                        "subject": "Senior Engineer position",
                        "snippet": "We have a position open.",
                        "unread": True,
                    },
                    {
                        "uid": "2",
                        "sender": "Billing <billing@example.com>",
                        "subject": "Your invoice is ready",
                        "snippet": "Nothing to do.",
                        "unread": True,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    # The MCP subprocesses re-read the config from this env var.
    monkeypatch.setenv("MAIL_A2A_CONFIG", str(path))
    return load_settings(path)


async def test_scan_notifies_every_new_message(settings):
    async with running_agents(settings):
        result = await run_scan(settings)

    assert result.error == ""
    assert result.scanned == 2
    assert result.new == 2
    assert result.notified == 2
    assert result.failed == 0
    # Only the recruiter email hits a configured keyword.
    assert result.priority == 1
    assert {item.uid for item in result.results} == {"1", "2"}
    assert all(item.ok and item.provider == "console" for item in result.results)


async def test_notification_text_carries_sender_subject_and_flag(settings):
    async with running_agents(settings):
        result = await run_scan(settings)

    by_uid = {item.uid: item.text for item in result.results}
    assert "TOP PRIORITY" in by_uid["1"]
    assert "Recruiter <talent@example.com>" in by_uid["1"]
    assert "Senior Engineer position" in by_uid["1"]
    assert "TOP PRIORITY" not in by_uid["2"]
    assert "Your invoice is ready" in by_uid["2"]


async def test_second_scan_does_not_renotify(settings):
    async with running_agents(settings):
        first = await run_scan(settings)
        second = await run_scan(settings)

    assert first.notified == 2
    assert second.scanned == 2
    assert second.new == 0
    assert second.notified == 0


async def test_agent_cards_are_published(settings):
    import httpx

    async with running_agents(settings):
        async with httpx.AsyncClient(timeout=5) as http:
            for endpoint, name, skill in (
                (settings.agents.mailbox, "mailbox-reader-agent", "scan_and_notify"),
                (settings.agents.whatsapp, "whatsapp-notifier-agent", "notify_whatsapp"),
            ):
                response = await http.get(f"{endpoint.url}/.well-known/agent-card.json")
                assert response.status_code == 200
                card = response.json()
                assert card["name"] == name
                assert [s["id"] for s in card["skills"]] == [skill]
                assert card["supportedInterfaces"][0]["protocolBinding"] == "JSONRPC"


async def test_notifier_agent_answers_a_direct_a2a_call(settings):
    """Agent 2 is independently addressable, not just reachable through agent 1."""
    async with running_agents(settings):
        async with open_a2a_client(settings.agents.whatsapp.url, timeout_seconds=60) as client:
            reply = await send_json(
                client,
                {
                    "uid": "99",
                    "sender": "Someone <a@b.com>",
                    "subject": "An opening you may like",
                    "priority": True,
                    "matched_keywords": ["opening"],
                },
                peer=settings.agents.whatsapp.url,
                skill="notify_whatsapp",
            )

    assert reply["ok"] is True
    assert reply["uid"] == "99"
    assert "TOP PRIORITY" in reply["text"]


async def test_malformed_a2a_request_is_reported_not_crashed(settings):
    async with running_agents(settings):
        async with open_a2a_client(settings.agents.whatsapp.url, timeout_seconds=60) as client:
            reply = await send_json(
                client,
                {"nonsense": True},
                peer=settings.agents.whatsapp.url,
                skill="notify_whatsapp",
            )

    assert reply["ok"] is False
    assert "invalid notify request" in reply["error"]


async def test_empty_mailbox_scan_is_a_no_op(settings, tmp_path):
    (tmp_path / "mail.json").write_text(json.dumps({"messages": []}), encoding="utf-8")
    async with running_agents(settings):
        result = await run_scan(settings)

    assert result == ScanResult(scanned=0, new=0, notified=0)
