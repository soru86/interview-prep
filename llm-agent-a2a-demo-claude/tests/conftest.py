import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _isolated_config(tmp_path, monkeypatch):
    """Never let a test read the developer's real config/config.yaml."""
    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.setenv("MAIL_A2A_CONFIG", str(tmp_path / "absent.yaml"))
    for key in list(os.environ):
        if key.startswith(("MAILBOX_", "WHATSAPP_", "META_WHATSAPP_", "TWILIO_", "OLLAMA_")):
            monkeypatch.delenv(key, raising=False)
    from mail_a2a.config import clear_settings_cache

    clear_settings_cache()
    yield
    clear_settings_cache()
