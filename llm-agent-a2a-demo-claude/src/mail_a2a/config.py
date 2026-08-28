"""Typed configuration loaded from config/config.yaml with env-var overrides.

The config file is the source of truth (that is what the brief asks for); the
environment is only there so secrets can stay out of the file and so spawned MCP
subprocesses inherit the same settings.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, ValidationError

DEFAULT_CONFIG_PATH = Path("config/config.yaml")
CONFIG_PATH_ENV = "MAIL_A2A_CONFIG"


class MailboxSettings(BaseModel):
    provider: Literal["imap", "demo"] = "demo"
    host: str = "outlook.office365.com"
    port: int = 993
    username: str = ""
    password: str = ""
    auth: Literal["password", "oauth2"] = "password"
    ssl: bool = True
    folder: str = "INBOX"
    unread_only: bool = True
    mark_seen: bool = False
    oauth_client_id: str = ""
    oauth_tenant: str = "consumers"
    oauth_token_cache: str = "data/state/msal_token.json"
    sample_file: str = "data/sample_emails.json"


class MetaWhatsAppSettings(BaseModel):
    access_token: str = ""
    phone_number_id: str = ""
    api_version: str = "v21.0"
    message_mode: Literal["text", "template"] = "text"
    template_name: str = "email_alert"
    template_language: str = "en"


class TwilioWhatsAppSettings(BaseModel):
    account_sid: str = ""
    auth_token: str = ""
    from_number: str = "whatsapp:+14155238886"


class WhatsAppSettings(BaseModel):
    provider: Literal["console", "meta", "twilio"] = "console"
    to: str = ""
    meta: MetaWhatsAppSettings = Field(default_factory=MetaWhatsAppSettings)
    twilio: TwilioWhatsAppSettings = Field(default_factory=TwilioWhatsAppSettings)


class OllamaSettings(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "deepseek-r1:1.5b"
    timeout_seconds: int = 180
    temperature: float = 0.2
    # DeepSeek R1 is a reasoning model; leaving `think` on empties message.content.
    think: bool = False
    required: bool = False


class AgentEndpoint(BaseModel):
    host: str = "127.0.0.1"
    port: int = 9101

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class AgentsSettings(BaseModel):
    mailbox: AgentEndpoint = Field(default_factory=lambda: AgentEndpoint(port=9101))
    whatsapp: AgentEndpoint = Field(default_factory=lambda: AgentEndpoint(port=9102))


class LoggingSettings(BaseModel):
    level: str = "INFO"
    file: str = "logs/agents.log"


class Settings(BaseModel):
    mailbox: MailboxSettings = Field(default_factory=MailboxSettings)
    whatsapp: WhatsAppSettings = Field(default_factory=WhatsAppSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    agents: AgentsSettings = Field(default_factory=AgentsSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    priority_keywords: list[str] = Field(
        default_factory=lambda: ["job", "opportunity", "opening", "position"]
    )
    max_emails: int = 10
    poll_interval_seconds: int = 60
    state_file: str = "data/state/seen.json"


# env var -> dotted path in the settings tree
_ENV_OVERRIDES: dict[str, str] = {
    "MAILBOX_PROVIDER": "mailbox.provider",
    "MAILBOX_HOST": "mailbox.host",
    "MAILBOX_PORT": "mailbox.port",
    "MAILBOX_USERNAME": "mailbox.username",
    "MAILBOX_PASSWORD": "mailbox.password",
    "MAILBOX_AUTH": "mailbox.auth",
    "MAILBOX_FOLDER": "mailbox.folder",
    "MAILBOX_OAUTH_CLIENT_ID": "mailbox.oauth_client_id",
    "MAILBOX_OAUTH_TENANT": "mailbox.oauth_tenant",
    "WHATSAPP_PROVIDER": "whatsapp.provider",
    "WHATSAPP_TO": "whatsapp.to",
    "META_WHATSAPP_ACCESS_TOKEN": "whatsapp.meta.access_token",
    "META_WHATSAPP_PHONE_NUMBER_ID": "whatsapp.meta.phone_number_id",
    "META_WHATSAPP_MESSAGE_MODE": "whatsapp.meta.message_mode",
    "META_WHATSAPP_TEMPLATE_NAME": "whatsapp.meta.template_name",
    "TWILIO_ACCOUNT_SID": "whatsapp.twilio.account_sid",
    "TWILIO_AUTH_TOKEN": "whatsapp.twilio.auth_token",
    "TWILIO_WHATSAPP_FROM": "whatsapp.twilio.from_number",
    "OLLAMA_BASE_URL": "ollama.base_url",
    "OLLAMA_MODEL": "ollama.model",
    "MAIL_A2A_LOG_LEVEL": "logging.level",
    "MAIL_A2A_LOG_FILE": "logging.file",
}

# Names an MCP subprocess needs to rebuild the same Settings as its parent.
PASSTHROUGH_ENV: tuple[str, ...] = (*_ENV_OVERRIDES.keys(), "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE")


def _assign(tree: dict[str, Any], dotted: str, value: str) -> None:
    parts = dotted.split(".")
    node = tree
    for part in parts[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = value


class ConfigError(ValueError):
    """A config file that cannot be parsed or validated, with a readable message."""


def _format_yaml_error(path: Path, text: str, exc: yaml.YAMLError) -> str:
    """Point at the offending line instead of dumping a parser traceback."""
    mark = getattr(exc, "problem_mark", None)
    problem = getattr(exc, "problem", None) or "invalid YAML"
    if mark is None:
        return f"{path}: {problem}"

    lines = text.splitlines()
    excerpt = ""
    if 0 <= mark.line < len(lines):
        offending = lines[mark.line]
        excerpt = f"\n  {mark.line + 1} | {offending}\n     {' ' * mark.column}^"

    hint = ""
    # By far the most common cause: a mapping key that lost its colon.
    if "could not find expected ':'" in problem:
        hint = "\n  hint: a key is missing its ':' — e.g. 'whatsapp' should be 'whatsapp:'"

    return f"{path}, line {mark.line + 1}, column {mark.column + 1}: {problem}{excerpt}{hint}"


def config_path() -> Path:
    return Path(os.environ.get(CONFIG_PATH_ENV) or DEFAULT_CONFIG_PATH)


def load_settings(path: Path | str | None = None) -> Settings:
    """Read YAML (if present), layer env overrides on top, validate."""
    target = Path(path) if path else config_path()
    raw: dict[str, Any] = {}
    if target.is_file():
        text = target.read_text(encoding="utf-8")
        try:
            loaded = yaml.safe_load(text) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(_format_yaml_error(target, text, exc)) from None
        if not isinstance(loaded, dict):
            raise ConfigError(f"{target} must contain a YAML mapping")
        raw = loaded

    for env_name, dotted in _ENV_OVERRIDES.items():
        value = os.environ.get(env_name)
        if value not in (None, ""):
            _assign(raw, dotted, value)

    try:
        return Settings.model_validate(raw)
    except ValidationError as exc:
        problems = "\n".join(
            f"  {'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        )
        raise ConfigError(f"{target} has invalid values:\n{problems}") from None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
