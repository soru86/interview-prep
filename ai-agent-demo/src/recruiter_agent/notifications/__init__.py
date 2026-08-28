from __future__ import annotations

from recruiter_agent.config import Settings
from recruiter_agent.notifications.whatsapp import (
    MetaWhatsAppNotifier,
    Notifier,
    NullNotifier,
    TwilioWhatsAppNotifier,
    WhatsAppMessageMode,
)

__all__ = [
    "MetaWhatsAppNotifier",
    "Notifier",
    "NullNotifier",
    "TwilioWhatsAppNotifier",
    "WhatsAppMessageMode",
    "build_notifier",
]


def build_notifier(settings: Settings) -> Notifier:
    provider = settings.whatsapp_provider.lower()

    if provider == "meta":
        return MetaWhatsAppNotifier(
            access_token=settings.meta_whatsapp_access_token,
            phone_number_id=settings.meta_whatsapp_phone_number_id,
            to_number=settings.whatsapp_to,
            api_version=settings.meta_whatsapp_api_version,
            message_mode=WhatsAppMessageMode(settings.meta_whatsapp_message_mode),
            template_name=settings.meta_whatsapp_template_name,
            template_language=settings.meta_whatsapp_template_language,
        )

    if provider == "twilio":
        return TwilioWhatsAppNotifier(
            account_sid=settings.twilio_account_sid,
            auth_token=settings.twilio_auth_token,
            from_number=settings.twilio_whatsapp_from,
            to_number=settings.whatsapp_to,
        )

    return NullNotifier()
