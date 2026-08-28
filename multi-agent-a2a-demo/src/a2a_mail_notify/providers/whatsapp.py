from __future__ import annotations

import re
from abc import ABC, abstractmethod
from enum import Enum

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from a2a_mail_notify.config import Settings
from a2a_mail_notify.logging import get_logger
from a2a_mail_notify.models import NotifyResult

log = get_logger(__name__)


class WhatsAppMessageMode(str, Enum):
    TEXT = "text"
    TEMPLATE = "template"


def normalize_phone_number(raw: str) -> str:
    cleaned = raw.removeprefix("whatsapp:").strip()
    return re.sub(r"\D", "", cleaned)


def build_alert_body(sender: str, subject: str, priority: bool, snippet: str = "") -> str:
    lines: list[str] = []
    if priority:
        lines.append("TOP PRIORITY")
    lines.extend(["New email", f"From: {sender}", f"Subject: {subject}"])
    if snippet:
        lines.append(snippet[:280])
    return "\n".join(lines)


def _truncate(value: str, max_len: int) -> str:
    value = (value or "-").strip() or "-"
    if len(value) <= max_len:
        return value
    return value[: max_len - 3] + "..."


class WhatsAppNotifier(ABC):
    provider_name: str = ""

    @abstractmethod
    async def send_notification(
        self,
        sender: str,
        subject: str,
        priority: bool,
        body: str,
    ) -> NotifyResult:
        raise NotImplementedError


class MetaWhatsAppNotifier(WhatsAppNotifier):
    provider_name = "meta"

    def __init__(
        self,
        access_token: str,
        phone_number_id: str,
        to_number: str,
        api_version: str = "v21.0",
        message_mode: WhatsAppMessageMode = WhatsAppMessageMode.TEMPLATE,
        template_name: str = "email_alert",
        template_language: str = "en",
    ) -> None:
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.to_number = normalize_phone_number(to_number)
        self.api_version = api_version
        self.message_mode = message_mode
        self.template_name = template_name
        self.template_language = template_language

    @property
    def _messages_url(self) -> str:
        return (
            f"https://graph.facebook.com/{self.api_version}/"
            f"{self.phone_number_id}/messages"
        )

    async def send_notification(
        self,
        sender: str,
        subject: str,
        priority: bool,
        body: str,
    ) -> NotifyResult:
        if not all([self.access_token, self.phone_number_id, self.to_number]):
            log.warning("whatsapp_skipped", reason="Meta WhatsApp credentials not configured")
            return NotifyResult(ok=False, provider="meta", error="credentials not configured")

        if self.message_mode == WhatsAppMessageMode.TEMPLATE:
            payload = self._build_template_payload(sender, subject, priority)
        else:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.to_number,
                "type": "text",
                "text": {"preview_url": False, "body": body},
            }

        message_id = await self._send(payload)
        log.info(
            "whatsapp_sent_meta",
            message_id=message_id,
            to=self.to_number,
            mode=self.message_mode.value,
            priority=priority,
        )
        return NotifyResult(ok=True, provider="meta", message_id=message_id, body=body)

    def _build_template_payload(self, sender: str, subject: str, priority: bool) -> dict:
        # Template body example (approve in Meta Business Manager as `email_alert`):
        # "{{1}} From: {{2}} Subject: {{3}}"
        flag = "TOP PRIORITY" if priority else "New email"
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.to_number,
            "type": "template",
            "template": {
                "name": self.template_name,
                "language": {"code": self.template_language},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": _truncate(flag, 60)},
                            {"type": "text", "text": _truncate(sender, 80)},
                            {"type": "text", "text": _truncate(subject, 120)},
                        ],
                    }
                ],
            },
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=15))
    async def _send(self, payload: dict) -> str:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(self._messages_url, json=payload, headers=headers)
            if response.is_error:
                log.error(
                    "meta_whatsapp_api_error",
                    status=response.status_code,
                    body=response.text,
                )
            response.raise_for_status()
            data = response.json()
            messages = data.get("messages", [])
            if not messages:
                raise ValueError(f"Unexpected Meta API response: {data}")
            return messages[0].get("id", "")


class TwilioWhatsAppNotifier(WhatsAppNotifier):
    provider_name = "twilio"

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_number: str,
        to_number: str,
    ) -> None:
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        if to_number and not to_number.startswith("whatsapp:"):
            digits = normalize_phone_number(to_number)
            self.to_number = f"whatsapp:+{digits}"
        else:
            self.to_number = to_number

    async def send_notification(
        self,
        sender: str,
        subject: str,
        priority: bool,
        body: str,
    ) -> NotifyResult:
        if not all([self.account_sid, self.auth_token, self.from_number, self.to_number]):
            log.warning("whatsapp_skipped", reason="Twilio credentials not configured")
            return NotifyResult(ok=False, provider="twilio", error="credentials not configured")

        from twilio.rest import Client

        client = Client(self.account_sid, self.auth_token)
        message = client.messages.create(
            body=body,
            from_=self.from_number,
            to=self.to_number,
        )
        log.info("whatsapp_sent_twilio", sid=message.sid, to=self.to_number, priority=priority)
        return NotifyResult(ok=True, provider="twilio", message_id=message.sid, body=body)


class DryRunNotifier(WhatsAppNotifier):
    provider_name = "dry_run"

    def __init__(self, inner_provider: str, to_number: str) -> None:
        self.inner_provider = inner_provider
        self.to_number = to_number

    async def send_notification(
        self,
        sender: str,
        subject: str,
        priority: bool,
        body: str,
    ) -> NotifyResult:
        log.info(
            "whatsapp_dry_run",
            provider=self.inner_provider,
            to=self.to_number,
            sender=sender,
            subject=subject,
            priority=priority,
            body=body,
        )
        return NotifyResult(
            ok=True,
            provider=self.inner_provider,
            dry_run=True,
            body=body,
        )


def build_notifier(settings: Settings) -> WhatsAppNotifier:
    provider = settings.whatsapp.provider.lower()
    if settings.dry_run:
        return DryRunNotifier(inner_provider=provider, to_number=settings.whatsapp.to)

    if provider == "twilio":
        return TwilioWhatsAppNotifier(
            account_sid=settings.whatsapp.twilio.account_sid,
            auth_token=settings.whatsapp.twilio.auth_token,
            from_number=settings.whatsapp.twilio.from_number,
            to_number=settings.whatsapp.to,
        )

    return MetaWhatsAppNotifier(
        access_token=settings.whatsapp.meta.access_token,
        phone_number_id=settings.whatsapp.meta.phone_number_id,
        to_number=settings.whatsapp.to,
        api_version=settings.whatsapp.meta.api_version,
        message_mode=WhatsAppMessageMode(settings.whatsapp.meta.message_mode),
        template_name=settings.whatsapp.meta.template_name,
        template_language=settings.whatsapp.meta.template_language,
    )
