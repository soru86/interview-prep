import email
import json

import httpx
import pytest

from mail_a2a.config import MailboxSettings, WhatsAppSettings
from mail_a2a.providers.mailbox import DemoMailbox, ImapMailbox, build_mailbox
from mail_a2a.providers.whatsapp import (
    ConsoleChannel,
    MetaCloudChannel,
    TwilioChannel,
    build_channel,
    explain_error,
    normalize_number,
)

# --- mailbox ----------------------------------------------------------------


def test_build_mailbox_honours_provider():
    assert isinstance(build_mailbox(MailboxSettings(provider="demo")), DemoMailbox)
    assert isinstance(build_mailbox(MailboxSettings(provider="imap")), ImapMailbox)


def test_demo_mailbox_reads_the_sample_file(tmp_path):
    path = tmp_path / "mail.json"
    path.write_text(
        json.dumps(
            {
                "messages": [
                    {"uid": "1", "sender": "A", "subject": "One", "unread": True},
                    {"uid": "2", "sender": "B", "subject": "Two", "unread": False},
                ]
            }
        ),
        encoding="utf-8",
    )
    mailbox = DemoMailbox(path)
    assert [m.uid for m in mailbox.list_messages(10, unread_only=True)] == ["1"]
    assert [m.uid for m in mailbox.list_messages(10, unread_only=False)] == ["1", "2"]
    assert mailbox.list_messages(1, unread_only=False)[0].uid == "1"


def test_demo_mailbox_survives_a_missing_file(tmp_path):
    mailbox = DemoMailbox(tmp_path / "gone.json")
    assert mailbox.list_messages(10, unread_only=True) == []
    assert mailbox.ping()["ok"] is False


def test_shipped_sample_file_parses():
    messages = DemoMailbox("data/sample_emails.json").list_messages(50, unread_only=False)
    assert len(messages) >= 6
    assert all(m.uid and m.sender and m.subject for m in messages)


RAW_EMAIL = b"""From: =?utf-8?q?Priya_Raman?= <priya@example.com>
Subject: =?utf-8?q?Senior_Engineer_position?=
Date: Sun, 16 Aug 2026 09:12:00 +0400
Content-Type: text/plain; charset="utf-8"

Hello, we have a position open on the platform team.
"""


def test_imap_summary_decodes_headers_and_body():
    summary = ImapMailbox._to_summary("42", email.message_from_bytes(RAW_EMAIL))
    assert summary.uid == "42"
    assert summary.sender == "Priya Raman <priya@example.com>"
    assert summary.sender_email == "priya@example.com"
    assert summary.subject == "Senior Engineer position"
    assert summary.received_at.startswith("2026-08-16T09:12:00")
    assert "position open on the platform team" in summary.snippet


MULTIPART_EMAIL = b"""From: Careers <jobs@example.com>
Subject: Opening
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="b"

--b
Content-Type: text/plain; charset="utf-8"

Plain text body.
--b
Content-Type: text/html; charset="utf-8"

<html><body><p>HTML body.</p></body></html>
--b--
"""


def test_imap_summary_prefers_plain_text_part():
    summary = ImapMailbox._to_summary("7", email.message_from_bytes(MULTIPART_EMAIL))
    assert "Plain text body." in summary.snippet
    assert "HTML body" not in summary.snippet


def test_imap_summary_falls_back_to_stripped_html():
    html_only = MULTIPART_EMAIL.replace(b"Content-Type: text/plain", b"Content-Type: text/x-other")
    summary = ImapMailbox._to_summary("8", email.message_from_bytes(html_only))
    assert "HTML body." in summary.snippet
    assert "<p>" not in summary.snippet


def test_imap_refuses_to_connect_without_a_password():
    mailbox = ImapMailbox(MailboxSettings(provider="imap", auth="password", password=""))
    with pytest.raises(RuntimeError, match="mailbox.password is empty"):
        mailbox.connect()


# --- whatsapp ---------------------------------------------------------------


def test_build_channel_honours_provider():
    assert isinstance(build_channel(WhatsAppSettings(provider="console")), ConsoleChannel)
    meta = WhatsAppSettings(provider="meta")
    meta.meta.access_token = "t"
    meta.meta.phone_number_id = "1"
    assert isinstance(build_channel(meta), MetaCloudChannel)


@pytest.mark.parametrize(
    "raw,expected",
    [("+971 56 889 6895", "971568896895"), ("971568896895", "971568896895")],
)
def test_normalize_number(raw, expected):
    assert normalize_number(raw) == expected


def test_meta_channel_requires_credentials():
    with pytest.raises(RuntimeError, match="meta.access_token"):
        MetaCloudChannel(WhatsAppSettings(provider="meta"))


def test_twilio_channel_requires_credentials():
    with pytest.raises(RuntimeError, match="twilio.account_sid"):
        TwilioChannel(WhatsAppSettings(provider="twilio"))


async def test_console_channel_always_succeeds():
    result = await ConsoleChannel().send("971568896895", "hello", priority=True)
    assert result == {
        "ok": True,
        "provider": "console",
        "to": "971568896895",
        "message_id": "console-dry-run",
    }


def _meta_settings(mode="text") -> WhatsAppSettings:
    settings = WhatsAppSettings(provider="meta", to="971568896895")
    settings.meta.access_token = "tok"
    settings.meta.phone_number_id = "555"
    settings.meta.message_mode = mode
    return settings


def test_meta_text_payload_shape():
    payload = MetaCloudChannel(_meta_settings())._payload("971568896895", "line one\nline two")
    assert payload["type"] == "text"
    assert payload["text"]["body"] == "line one\nline two"


def test_meta_template_payload_flattens_newlines():
    # Meta rejects newlines inside template parameters.
    payload = MetaCloudChannel(_meta_settings("template"))._payload("971", "line one\nline two")
    assert payload["type"] == "template"
    param = payload["template"]["components"][0]["parameters"][0]["text"]
    assert "\n" not in param
    assert param == "line one line two"


@pytest.fixture
def mock_transport(monkeypatch):
    def install(handler):
        transport = httpx.MockTransport(handler)
        original_init = httpx.AsyncClient.__init__

        def patched_init(self, *args, **kwargs):
            kwargs["transport"] = transport
            original_init(self, *args, **kwargs)

        monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)

    return install


async def test_meta_send_returns_message_id(mock_transport):
    mock_transport(
        lambda request: httpx.Response(200, json={"messages": [{"id": "wamid.123"}]})
    )
    result = await MetaCloudChannel(_meta_settings()).send("+971 56 889 6895", "hi")
    assert result["ok"] is True
    assert result["message_id"] == "wamid.123"
    assert result["to"] == "971568896895"


async def test_meta_send_reports_api_rejection(mock_transport):
    mock_transport(
        lambda request: httpx.Response(400, json={"error": {"message": "outside 24h window"}})
    )
    result = await MetaCloudChannel(_meta_settings()).send("971568896895", "hi")
    assert result["ok"] is False
    assert "outside 24h window" in result["error"]


EXPIRED_TOKEN_BODY = {
    "error": {
        "message": "Error validating access token: Session has expired on Friday, 14-Aug-26",
        "type": "OAuthException",
        "code": 190,
        "error_subcode": 463,
    }
}


@pytest.mark.parametrize(
    "body,expected",
    [
        (EXPIRED_TOKEN_BODY, "expired"),
        ({"error": {"code": 190, "message": "Invalid OAuth access token"}}, "invalid"),
        ({"error": {"code": 131047}}, "24-hour customer-care window"),
        ({"error": {"code": 131030}}, "allowed test-number list"),
        ({"error": {"code": 100, "error_subcode": 33}}, "not a Phone Number ID"),
        ({"error": {"code": 999}}, ""),
        ({}, ""),
    ],
)
def test_explain_error_gives_actionable_hints(body, expected):
    assert expected in explain_error(body)


async def test_meta_send_explains_an_expired_token(mock_transport):
    mock_transport(lambda request: httpx.Response(401, json=EXPIRED_TOKEN_BODY))
    result = await MetaCloudChannel(_meta_settings()).send("971568896895", "hi")
    assert result["ok"] is False
    # The raw Meta payload alone does not tell you the token needs reissuing.
    assert "expired" in result["error"]
    assert "System User token" in result["error"]


async def test_meta_verify_detects_an_expired_token(mock_transport):
    mock_transport(lambda request: httpx.Response(401, json=EXPIRED_TOKEN_BODY))
    result = await MetaCloudChannel(_meta_settings()).verify()
    assert result["ok"] is False
    assert "expired" in result["error"]


async def test_meta_verify_accepts_a_live_token(mock_transport):
    mock_transport(
        lambda request: httpx.Response(200, json={"display_phone_number": "+971 55 000 0000"})
    )
    result = await MetaCloudChannel(_meta_settings()).verify()
    assert result["ok"] is True
    assert result["sender_number"] == "+971 55 000 0000"


async def test_console_channel_verifies_without_credentials():
    assert (await ConsoleChannel().verify())["ok"] is True


async def test_twilio_send_formats_addresses(mock_transport):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = request.content.decode()
        return httpx.Response(201, json={"sid": "SM123"})

    mock_transport(handler)
    settings = WhatsAppSettings(provider="twilio", to="971568896895")
    settings.twilio.account_sid = "AC1"
    settings.twilio.auth_token = "tok"
    result = await TwilioChannel(settings).send("971568896895", "hi")
    assert result["ok"] is True
    assert result["message_id"] == "SM123"
    assert "whatsapp" in seen["body"]
