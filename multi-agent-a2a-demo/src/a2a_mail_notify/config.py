from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class MailboxSettings(BaseModel):
    host: str = "imap.gmail.com"
    port: int = 993
    username: str = ""
    password: str = ""
    folder: str = "INBOX"
    ssl: bool = True
    unread_only: bool = True
    # password = IMAP LOGIN (Gmail app password). oauth2 = Outlook.com / Microsoft 365 XOAUTH2.
    auth: str = "password"
    oauth_client_id: str = ""
    oauth_tenant: str = "consumers"
    oauth_token_cache: Path = Path("data/state/msal_token.json")


class MetaWhatsAppSettings(BaseModel):
    access_token: str = ""
    phone_number_id: str = ""
    api_version: str = "v21.0"
    message_mode: str = "template"
    template_name: str = "email_alert"
    template_language: str = "en"


class TwilioWhatsAppSettings(BaseModel):
    account_sid: str = ""
    auth_token: str = ""
    from_number: str = ""


class WhatsAppSettings(BaseModel):
    provider: str = "meta"
    to: str = ""
    meta: MetaWhatsAppSettings = Field(default_factory=MetaWhatsAppSettings)
    twilio: TwilioWhatsAppSettings = Field(default_factory=TwilioWhatsAppSettings)


class OllamaSettings(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "deepseek-r1:1.5b"
    timeout_seconds: int = 180


class AgentEndpoint(BaseModel):
    host: str = "127.0.0.1"
    port: int = 9000

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class AgentsSettings(BaseModel):
    mailbox: AgentEndpoint = Field(default_factory=lambda: AgentEndpoint(port=9001))
    whatsapp: AgentEndpoint = Field(default_factory=lambda: AgentEndpoint(port=9002))


class LoggingSettings(BaseModel):
    level: str = "INFO"
    file: Path = Path("logs/agents.log")


class Settings(BaseModel):
    mailbox: MailboxSettings = Field(default_factory=MailboxSettings)
    whatsapp: WhatsAppSettings = Field(default_factory=WhatsAppSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    agents: AgentsSettings = Field(default_factory=AgentsSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    priority_keywords: list[str] = Field(
        default_factory=lambda: ["job", "opportunity", "opening", "position"]
    )
    dry_run: bool = False
    poll_interval_seconds: int = 5
    max_emails: int = 20
    state_db_path: Path = Path("data/state/agent.db")
    config_path: Path = Path("config/config.yaml")


def _apply_env_overrides(data: dict[str, Any]) -> dict[str, Any]:
    mailbox = data.setdefault("mailbox", {})
    whatsapp = data.setdefault("whatsapp", {})
    meta = whatsapp.setdefault("meta", {})
    twilio = whatsapp.setdefault("twilio", {})
    ollama = data.setdefault("ollama", {})
    logging_cfg = data.setdefault("logging", {})

    env_map = {
        "MAILBOX_HOST": ("mailbox", "host"),
        "MAILBOX_PORT": ("mailbox", "port"),
        "MAILBOX_USERNAME": ("mailbox", "username"),
        "MAILBOX_PASSWORD": ("mailbox", "password"),
        "MAILBOX_FOLDER": ("mailbox", "folder"),
        "MAILBOX_AUTH": ("mailbox", "auth"),
        "MAILBOX_OAUTH_CLIENT_ID": ("mailbox", "oauth_client_id"),
        "MAILBOX_OAUTH_TENANT": ("mailbox", "oauth_tenant"),
        "WHATSAPP_PROVIDER": ("whatsapp", "provider"),
        "WHATSAPP_TO": ("whatsapp", "to"),
        "META_WHATSAPP_ACCESS_TOKEN": ("meta", "access_token"),
        "META_WHATSAPP_PHONE_NUMBER_ID": ("meta", "phone_number_id"),
        "META_WHATSAPP_API_VERSION": ("meta", "api_version"),
        "META_WHATSAPP_MESSAGE_MODE": ("meta", "message_mode"),
        "META_WHATSAPP_TEMPLATE_NAME": ("meta", "template_name"),
        "TWILIO_ACCOUNT_SID": ("twilio", "account_sid"),
        "TWILIO_AUTH_TOKEN": ("twilio", "auth_token"),
        "TWILIO_WHATSAPP_FROM": ("twilio", "from_number"),
        "OLLAMA_BASE_URL": ("ollama", "base_url"),
        "OLLAMA_MODEL": ("ollama", "model"),
        "LOG_LEVEL": ("logging", "level"),
        "DRY_RUN": ("root", "dry_run"),
    }

    buckets = {
        "mailbox": mailbox,
        "whatsapp": whatsapp,
        "meta": meta,
        "twilio": twilio,
        "ollama": ollama,
        "logging": logging_cfg,
        "root": data,
    }

    for env_name, (bucket, key) in env_map.items():
        value = os.environ.get(env_name)
        if value is None or value == "":
            continue
        if key in {"port"}:
            buckets[bucket][key] = int(value)
        elif key in {"dry_run"}:
            buckets[bucket][key] = value.lower() in {"1", "true", "yes", "on"}
        else:
            buckets[bucket][key] = value
    return data


def resolve_config_path(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit
    env_path = os.environ.get("A2A_CONFIG_PATH")
    if env_path:
        return Path(env_path)
    return Path("config/config.yaml")


def load_settings(config_path: Path | None = None) -> Settings:
    path = resolve_config_path(config_path)
    data: dict[str, Any] = {}
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    data = _apply_env_overrides(data)
    settings = Settings.model_validate(data)
    settings.config_path = path
    return settings


@lru_cache
def get_settings() -> Settings:
    return load_settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
