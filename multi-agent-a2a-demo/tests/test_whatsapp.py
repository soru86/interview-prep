import pytest

from a2a_mail_notify.providers.whatsapp import (
    MetaWhatsAppNotifier,
    WhatsAppMessageMode,
    build_alert_body,
    build_notifier,
    normalize_phone_number,
)


def test_normalize_and_alert_body():
    assert normalize_phone_number("whatsapp:+971-56-889-6895") == "971568896895"
    body = build_alert_body("Ada <ada@x.com>", "Job opening", True, "Come work with us")
    assert body.startswith("TOP PRIORITY")
    assert "From: Ada <ada@x.com>" in body
    assert "Subject: Job opening" in body


@pytest.mark.asyncio
async def test_meta_text_send(httpx_mock, tmp_config):
    httpx_mock.add_response(
        url="https://graph.facebook.com/v21.0/12345/messages",
        json={"messages": [{"id": "wamid.123"}]},
    )
    notifier = MetaWhatsAppNotifier(
        access_token="test-token",
        phone_number_id="12345",
        to_number="971568896895",
        message_mode=WhatsAppMessageMode.TEXT,
    )
    result = await notifier.send_notification("Ada", "Hello", False, "New email\nFrom: Ada")
    assert result.ok is True
    assert result.message_id == "wamid.123"
    request = httpx_mock.get_request()
    assert request.headers["Authorization"] == "Bearer test-token"


def test_dry_run_notifier_from_settings(tmp_config):
    from a2a_mail_notify.config import load_settings

    settings = load_settings()
    notifier = build_notifier(settings)
    assert notifier.provider_name == "dry_run"
