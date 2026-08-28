"""WhatsApp delivery channels.

Three providers behind one interface:

* `console` — logs the message instead of sending. Default, so the demo runs
  end to end with no credentials and no risk of messaging a real number.
* `meta`    — WhatsApp Cloud API (graph.facebook.com).
* `twilio`  — Twilio's WhatsApp API, including their sandbox number.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any

import httpx

from mail_a2a.config import WhatsAppSettings
from mail_a2a.logging_setup import get_logger

log = get_logger(__name__)

_NON_DIGITS = re.compile(r"\D")


def normalize_number(number: str) -> str:
    """WhatsApp wants digits only, in international format, with no leading '+'."""
    return _NON_DIGITS.sub("", number or "")


def _json_or_empty(response: httpx.Response) -> dict[str, Any]:
    try:
        body = response.json()
        return body if isinstance(body, dict) else {}
    except ValueError:
        return {}


def explain_error(body: dict[str, Any]) -> str:
    """Turn a provider error body into an actionable hint, where we know one."""
    error = body.get("error") or {}
    code = error.get("code")
    subcode = error.get("error_subcode")
    if code == 190:
        detail = error.get("message", "")
        if subcode == 463 or "expired" in detail.lower():
            return (
                "the Meta access token has expired. Temporary tokens from the Meta "
                "dashboard last 24 hours — issue a System User token for a permanent one "
                "(see README, 'WhatsApp')"
            )
        return "the Meta access token is invalid or belongs to a different app"
    if code == 131047:
        return (
            "outside the 24-hour customer-care window: free-form text is not delivered. "
            "Set whatsapp.meta.message_mode to 'template' with an approved template"
        )
    if code == 131030:
        return "the recipient number is not in the app's allowed test-number list"
    if code == 100 and subcode == 33:
        return (
            "whatsapp.meta.phone_number_id is not a Phone Number ID the token can reach. "
            "Take it from WhatsApp Manager > API Setup — it is not the System User ID and "
            "not the WhatsApp Business Account ID"
        )
    return ""


class WhatsAppChannel(ABC):
    name: str = "unknown"

    @abstractmethod
    async def send(self, to: str, text: str, *, priority: bool = False) -> dict[str, Any]:
        """Deliver `text` to `to`. Returns {ok, message_id, error, ...}."""

    async def verify(self) -> dict[str, Any]:
        """Check credentials before a scan spends time on inference."""
        return {"ok": True, "provider": self.name}

    def describe(self) -> dict[str, Any]:
        return {"provider": self.name}


class ConsoleChannel(WhatsAppChannel):
    """Dry-run channel: records what would have been sent."""

    name = "console"

    async def send(self, to: str, text: str, *, priority: bool = False) -> dict[str, Any]:
        banner = "TOP PRIORITY " if priority else ""
        log.info(
            "whatsapp_console_send",
            to=to,
            priority=priority,
            text=text,
        )
        print(f"\n--- {banner}WhatsApp -> {to} ---\n{text}\n---\n", flush=True)
        return {"ok": True, "provider": self.name, "to": to, "message_id": "console-dry-run"}


class MetaCloudChannel(WhatsAppChannel):
    """WhatsApp Cloud API.

    Note the 24-hour rule: free-form `text` messages are only delivered if the
    recipient messaged the business in the last 24h. Outside that window Meta
    requires an approved template, hence `message_mode: template`.
    """

    name = "meta"

    def __init__(self, settings: WhatsAppSettings) -> None:
        self.cfg = settings.meta
        if not self.cfg.access_token or not self.cfg.phone_number_id:
            raise RuntimeError(
                "whatsapp.provider is 'meta' but meta.access_token / meta.phone_number_id "
                "are empty. Fill them in config/config.yaml or set "
                "META_WHATSAPP_ACCESS_TOKEN / META_WHATSAPP_PHONE_NUMBER_ID."
            )
        self.endpoint = (
            f"https://graph.facebook.com/{self.cfg.api_version}"
            f"/{self.cfg.phone_number_id}/messages"
        )

    async def verify(self) -> dict[str, Any]:
        """Confirm the access token is still valid.

        Meta's dashboard tokens expire after 24 hours, which otherwise surfaces
        only after a scan has already paid for LLM inference on every email.
        """
        headers = {"Authorization": f"Bearer {self.cfg.access_token}"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    f"https://graph.facebook.com/{self.cfg.api_version}/"
                    f"{self.cfg.phone_number_id}",
                    headers=headers,
                )
        except Exception as exc:
            return {"ok": False, "provider": self.name, "error": str(exc)}

        if response.status_code >= 400:
            body = _json_or_empty(response)
            hint = explain_error(body)
            return {
                "ok": False,
                "provider": self.name,
                "error": hint or (body.get("error") or {}).get("message", response.text[:300]),
            }
        return {
            "ok": True,
            "provider": self.name,
            "sender_number": response.json().get("display_phone_number", ""),
        }

    def _payload(self, to: str, text: str) -> dict[str, Any]:
        if self.cfg.message_mode == "template":
            return {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": self.cfg.template_name,
                    "language": {"code": self.cfg.template_language},
                    "components": [
                        {
                            "type": "body",
                            # Meta rejects newlines and tabs in template params.
                            "parameters": [{"type": "text", "text": " ".join(text.split())}],
                        }
                    ],
                },
            }
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }

    async def send(self, to: str, text: str, *, priority: bool = False) -> dict[str, Any]:
        to = normalize_number(to)
        payload = self._payload(to, text)
        headers = {"Authorization": f"Bearer {self.cfg.access_token}"}
        log.info("whatsapp_send_start", provider=self.name, to=to, mode=self.cfg.message_mode)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.endpoint, json=payload, headers=headers)
        except Exception as exc:
            log.error("whatsapp_send_failed", provider=self.name, to=to, error=str(exc))
            return {"ok": False, "provider": self.name, "to": to, "error": str(exc)}

        if response.status_code >= 400:
            detail = response.text[:500]
            hint = explain_error(_json_or_empty(response))
            log.error(
                "whatsapp_send_rejected",
                provider=self.name,
                to=to,
                status=response.status_code,
                hint=hint or None,
                detail=detail,
            )
            return {
                "ok": False,
                "provider": self.name,
                "to": to,
                "error": f"{hint} ({detail})" if hint else f"HTTP {response.status_code}: {detail}",
            }

        body = response.json()
        message_id = (body.get("messages") or [{}])[0].get("id", "")
        log.info("whatsapp_send_ok", provider=self.name, to=to, message_id=message_id)
        return {"ok": True, "provider": self.name, "to": to, "message_id": message_id}


class TwilioChannel(WhatsAppChannel):
    """Twilio WhatsApp API over its REST endpoint (no SDK dependency needed)."""

    name = "twilio"

    def __init__(self, settings: WhatsAppSettings) -> None:
        self.cfg = settings.twilio
        if not self.cfg.account_sid or not self.cfg.auth_token:
            raise RuntimeError(
                "whatsapp.provider is 'twilio' but twilio.account_sid / twilio.auth_token "
                "are empty. Fill them in config/config.yaml or set "
                "TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN."
            )
        self.endpoint = (
            f"https://api.twilio.com/2010-04-01/Accounts/{self.cfg.account_sid}/Messages.json"
        )

    @staticmethod
    def _whatsapp_address(number: str) -> str:
        if number.startswith("whatsapp:"):
            return number
        digits = normalize_number(number)
        return f"whatsapp:+{digits}"

    async def send(self, to: str, text: str, *, priority: bool = False) -> dict[str, Any]:
        destination = self._whatsapp_address(to)
        data = {
            "From": self._whatsapp_address(self.cfg.from_number),
            "To": destination,
            "Body": text,
        }
        log.info("whatsapp_send_start", provider=self.name, to=destination)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.endpoint,
                    data=data,
                    auth=(self.cfg.account_sid, self.cfg.auth_token),
                )
        except Exception as exc:
            log.error("whatsapp_send_failed", provider=self.name, to=destination, error=str(exc))
            return {"ok": False, "provider": self.name, "to": destination, "error": str(exc)}

        if response.status_code >= 400:
            detail = response.text[:500]
            log.error(
                "whatsapp_send_rejected",
                provider=self.name,
                to=destination,
                status=response.status_code,
                detail=detail,
            )
            return {
                "ok": False,
                "provider": self.name,
                "to": destination,
                "error": f"HTTP {response.status_code}: {detail}",
            }

        body = response.json()
        log.info("whatsapp_send_ok", provider=self.name, to=destination, message_id=body.get("sid"))
        return {
            "ok": True,
            "provider": self.name,
            "to": destination,
            "message_id": body.get("sid", ""),
        }


def build_channel(settings: WhatsAppSettings) -> WhatsAppChannel:
    if settings.provider == "meta":
        return MetaCloudChannel(settings)
    if settings.provider == "twilio":
        return TwilioChannel(settings)
    return ConsoleChannel()
