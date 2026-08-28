import pytest
import httpx

from recruiter_agent.notifications.whatsapp import (
    MetaWhatsAppNotifier,
    WhatsAppMessageMode,
    build_draft_notification_body,
    normalize_phone_number,
)


def test_normalize_phone_number():
    assert normalize_phone_number("whatsapp:+971568896895") == "971568896895"
    assert normalize_phone_number("+971 568 896 895") == "971568896895"


def test_build_draft_notification_body():
    body = build_draft_notification_body("Jane", "Engineer", "Acme", 85, "Role at Acme")
    assert "Jane" in body
    assert "85%" in body


@pytest.mark.asyncio
async def test_meta_whatsapp_template_send(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://graph.facebook.com/v21.0/123456/messages",
        json={"messages": [{"id": "wamid.test123"}]},
    )

    notifier = MetaWhatsAppNotifier(
        access_token="test-token",
        phone_number_id="123456",
        to_number="971568896895",
        message_mode=WhatsAppMessageMode.TEMPLATE,
        template_name="recruiter_draft_alert",
    )
    await notifier.send_draft_notification(
        recruiter_name="Jane Doe",
        role_title="Backend Engineer",
        company="Acme Corp",
        match_score=82,
        subject="Backend role at Acme",
    )

    request = httpx_mock.get_request()
    assert request is not None
    payload = request.read()
    assert b"recruiter_draft_alert" in payload
    assert b"971568896895" in payload


@pytest.mark.asyncio
async def test_meta_whatsapp_text_send(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://graph.facebook.com/v21.0/999/messages",
        json={"messages": [{"id": "wamid.text456"}]},
    )

    notifier = MetaWhatsAppNotifier(
        access_token="test-token",
        phone_number_id="999",
        to_number="971568896895",
        message_mode=WhatsAppMessageMode.TEXT,
    )
    await notifier.send_draft_notification(
        recruiter_name="Jane",
        role_title="Engineer",
        company="Acme",
        match_score=90,
        subject="Test",
    )

    request = httpx_mock.get_request()
    payload = request.read()
    assert b'"type": "text"' in payload or b'"type":"text"' in payload
