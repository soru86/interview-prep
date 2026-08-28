from __future__ import annotations

import re
from abc import ABC, abstractmethod
from enum import Enum

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from recruiter_agent.utils.logging import get_logger

log = get_logger(__name__)


class WhatsAppMessageMode(str, Enum):
    TEXT = "text"
    TEMPLATE = "template"


class Notifier(ABC):
    @abstractmethod
    async def send_draft_notification(
        self,
        recruiter_name: str,
        role_title: str,
        company: str,
        match_score: int,
        subject: str,
    ) -> None:
        raise NotImplementedError


def normalize_phone_number(raw: str) -> str:
    """Return digits-only E.164 number for Meta API (e.g. 971568896895)."""
    cleaned = raw.removeprefix("whatsapp:").strip()
    return re.sub(r"\D", "", cleaned)


def build_draft_notification_body(
    recruiter_name: str,
    role_title: str,
    company: str,
    match_score: int,
    subject: str,
) -> str:
    return (
        "Recruiter Agent: draft created\n"
        f"Recruiter: {recruiter_name}\n"
        f"Role: {role_title}\n"
        f"Company: {company}\n"
        f"Match: {match_score}%\n"
        f"Subject: {subject}\n"
        "Review the draft in Gmail before sending."
    )


class MetaWhatsAppNotifier(Notifier):
    """
    Meta WhatsApp Business Cloud API notifier.

    Production outbound alerts require an approved message template (message_mode=template).
    Free-form text works only inside the 24-hour customer service window (message_mode=text).
    Docs: https://developers.facebook.com/docs/whatsapp/cloud-api
    """

    def __init__(
        self,
        access_token: str,
        phone_number_id: str,
        to_number: str,
        api_version: str = "v21.0",
        message_mode: WhatsAppMessageMode = WhatsAppMessageMode.TEMPLATE,
        template_name: str = "recruiter_draft_alert",
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

    async def send_draft_notification(
        self,
        recruiter_name: str,
        role_title: str,
        company: str,
        match_score: int,
        subject: str,
    ) -> None:
        if not all([self.access_token, self.phone_number_id, self.to_number]):
            log.warning("whatsapp_skipped", reason="Meta WhatsApp credentials not configured")
            return

        if self.message_mode == WhatsAppMessageMode.TEMPLATE:
            payload = self._build_template_payload(
                recruiter_name, role_title, company, match_score, subject
            )
        else:
            payload = self._build_text_payload(
                recruiter_name, role_title, company, match_score, subject
            )

        message_id = await self._send(payload)
        log.info(
            "whatsapp_sent_meta",
            message_id=message_id,
            to=self.to_number,
            mode=self.message_mode.value,
        )

    def _build_text_payload(
        self,
        recruiter_name: str,
        role_title: str,
        company: str,
        match_score: int,
        subject: str,
    ) -> dict:
        body = build_draft_notification_body(
            recruiter_name, role_title, company, match_score, subject
        )
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.to_number,
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }

    def _build_template_payload(
        self,
        recruiter_name: str,
        role_title: str,
        company: str,
        match_score: int,
        subject: str,
    ) -> dict:
        # Template body example (create & approve in Meta Business Manager):
        # "Recruiter Agent: draft created for {{1}} at {{2}}.
        #  Role: {{3}} | Match: {{4}}% | Subject: {{5}}. Review in Gmail before sending."
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
                            {"type": "text", "text": _truncate(recruiter_name, 60)},
                            {"type": "text", "text": _truncate(company, 60)},
                            {"type": "text", "text": _truncate(role_title, 80)},
                            {"type": "text", "text": str(match_score)},
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


class TwilioWhatsAppNotifier(Notifier):
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
        self.to_number = to_number

    async def send_draft_notification(
        self,
        recruiter_name: str,
        role_title: str,
        company: str,
        match_score: int,
        subject: str,
    ) -> None:
        if not all([self.account_sid, self.auth_token, self.from_number, self.to_number]):
            log.warning("whatsapp_skipped", reason="Twilio credentials not configured")
            return

        body = build_draft_notification_body(
            recruiter_name, role_title, company, match_score, subject
        )

        from twilio.rest import Client

        client = Client(self.account_sid, self.auth_token)
        message = client.messages.create(
            body=body,
            from_=self.from_number,
            to=self.to_number,
        )
        log.info("whatsapp_sent_twilio", sid=message.sid, to=self.to_number)


class NullNotifier(Notifier):
    async def send_draft_notification(
        self,
        recruiter_name: str,
        role_title: str,
        company: str,
        match_score: int,
        subject: str,
    ) -> None:
        log.info(
            "whatsapp_skipped_null_notifier",
            recruiter=recruiter_name,
            role=role_title,
        )


def _truncate(value: str, max_len: int) -> str:
    value = value.strip() or "-"
    if len(value) <= max_len:
        return value
    return value[: max_len - 3] + "..."
