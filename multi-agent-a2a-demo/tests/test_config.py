from a2a_mail_notify.config import clear_settings_cache, load_settings


def test_load_yaml_and_env_override(tmp_config, monkeypatch):
    monkeypatch.setenv("MAILBOX_PASSWORD", "from-env")
    monkeypatch.setenv("WHATSAPP_TO", "15551212")
    monkeypatch.setenv("DRY_RUN", "false")
    clear_settings_cache()
    settings = load_settings()
    assert settings.mailbox.username == "user@example.com"
    assert settings.mailbox.password == "from-env"
    assert settings.whatsapp.to == "15551212"
    assert settings.dry_run is False
    assert settings.ollama.model == "deepseek-r1:1.5b"
    assert "job" in settings.priority_keywords
