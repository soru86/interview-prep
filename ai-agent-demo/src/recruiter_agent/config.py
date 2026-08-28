from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    email_provider: str = "gmail"
    gmail_credentials_path: Path = Path("./credentials.json")
    gmail_token_path: Path = Path("./token.json")
    gmail_recruiter_label: str = "Recruiters"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-r1:8b"
    ollama_timeout_seconds: int = 300

    resume_folder: Path = Path("./data/resume")
    tracker_path: Path = Path("./data/tracker/recruiter_tracker.xlsx")
    state_db_path: Path = Path("./data/state/agent.db")
    config_path: Path = Path("./config/settings.yaml")

    match_threshold: int = 70
    dry_run: bool = False
    auto_send: bool = False

    whatsapp_provider: str = "meta"
    whatsapp_to: str = "971568896895"

    meta_whatsapp_access_token: str = ""
    meta_whatsapp_phone_number_id: str = ""
    meta_whatsapp_api_version: str = "v21.0"
    meta_whatsapp_message_mode: str = "template"
    meta_whatsapp_template_name: str = "recruiter_draft_alert"
    meta_whatsapp_template_language: str = "en"

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""

    log_level: str = "INFO"

    recruiter_keywords: list[str] = Field(default_factory=list)
    recruiter_domains: list[str] = Field(default_factory=list)
    excel_columns: list[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if self.config_path.exists():
            with self.config_path.open(encoding="utf-8") as handle:
                yaml_config = yaml.safe_load(handle) or {}
            if not self.recruiter_keywords:
                self.recruiter_keywords = yaml_config.get("recruiter_keywords", [])
            if not self.recruiter_domains:
                self.recruiter_domains = yaml_config.get("recruiter_domains", [])
            if not self.excel_columns:
                self.excel_columns = yaml_config.get("excel_columns", [])


@lru_cache
def get_settings() -> Settings:
    return Settings()
