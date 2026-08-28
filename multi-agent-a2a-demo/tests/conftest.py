from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from a2a_mail_notify.config import clear_settings_cache, load_settings
from a2a_mail_notify.logging import configure_logging


@pytest.fixture
def tmp_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config = {
        "mailbox": {
            "host": "imap.example.com",
            "port": 993,
            "username": "user@example.com",
            "password": "secret-pass",
            "folder": "INBOX",
            "ssl": True,
            "unread_only": True,
        },
        "whatsapp": {
            "provider": "meta",
            "to": "971568896895",
            "meta": {
                "access_token": "test-token",
                "phone_number_id": "12345",
                "message_mode": "text",
                "template_name": "email_alert",
            },
        },
        "ollama": {"base_url": "http://localhost:11434", "model": "deepseek-r1:1.5b"},
        "priority_keywords": ["job", "opportunity", "opening", "position"],
        "dry_run": True,
        "max_emails": 10,
        "state_db_path": str(tmp_path / "state.db"),
        "logging": {"level": "INFO", "file": str(tmp_path / "agents.log")},
    }
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    monkeypatch.setenv("A2A_CONFIG_PATH", str(path))
    clear_settings_cache()
    configure_logging("INFO", tmp_path / "agents.log")
    yield path
    clear_settings_cache()
