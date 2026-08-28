import pytest

from mail_a2a.config import ConfigError, load_settings
from mail_a2a.logging_setup import redact


def _write(tmp_path, body: str):
    path = tmp_path / "config.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_defaults_apply_when_file_is_absent(tmp_path):
    settings = load_settings(tmp_path / "nope.yaml")
    assert settings.mailbox.provider == "demo"
    assert settings.whatsapp.provider == "console"
    assert settings.ollama.model == "deepseek-r1:1.5b"
    assert settings.priority_keywords == ["job", "opportunity", "opening", "position"]


def test_yaml_values_are_loaded(tmp_path):
    path = _write(
        tmp_path,
        """
mailbox:
  provider: imap
  host: imap.gmail.com
  username: me@gmail.com
  password: secret
whatsapp:
  provider: twilio
  to: "971500000000"
priority_keywords: [interview]
max_emails: 3
""",
    )
    settings = load_settings(path)
    assert settings.mailbox.host == "imap.gmail.com"
    assert settings.mailbox.password == "secret"
    assert settings.whatsapp.provider == "twilio"
    assert settings.whatsapp.to == "971500000000"
    assert settings.priority_keywords == ["interview"]
    assert settings.max_emails == 3


def test_env_overrides_yaml(tmp_path, monkeypatch):
    path = _write(tmp_path, "whatsapp:\n  to: '111'\n  provider: console\n")
    monkeypatch.setenv("WHATSAPP_TO", "999888777")
    monkeypatch.setenv("META_WHATSAPP_ACCESS_TOKEN", "tok")
    settings = load_settings(path)
    assert settings.whatsapp.to == "999888777"
    assert settings.whatsapp.meta.access_token == "tok"


def test_agent_endpoint_url_is_derived(tmp_path):
    path = _write(tmp_path, "agents:\n  mailbox:\n    host: 0.0.0.0\n    port: 8000\n")
    assert load_settings(path).agents.mailbox.url == "http://0.0.0.0:8000"


def test_invalid_provider_is_rejected(tmp_path):
    path = _write(tmp_path, "whatsapp:\n  provider: telegram\n")
    with pytest.raises(ConfigError) as exc:
        load_settings(path)
    assert "whatsapp.provider" in str(exc.value)
    assert "'console', 'meta' or 'twilio'" in str(exc.value)


def test_all_invalid_values_are_listed_at_once(tmp_path):
    path = _write(tmp_path, "whatsapp:\n  provider: telegram\nmax_emails: lots\n")
    message = str(pytest.raises(ConfigError, load_settings, path).value)
    assert "whatsapp.provider" in message
    assert "max_emails" in message


def test_non_mapping_yaml_is_rejected(tmp_path):
    path = _write(tmp_path, "- just\n- a list\n")
    with pytest.raises(ConfigError, match="must contain a YAML mapping"):
        load_settings(path)


def test_missing_colon_reports_file_line_and_hint(tmp_path):
    # The exact typo that produces an unreadable pyyaml traceback.
    path = _write(tmp_path, "mailbox:\n  provider: demo\n\nwhatsapp\n  provider: console\n")
    message = str(pytest.raises(ConfigError, load_settings, path).value)
    assert str(path) in message
    assert "could not find expected ':'" in message
    assert "provider: console" in message  # the offending line is quoted back
    assert "hint:" in message


def test_yaml_error_without_a_mark_still_reports_the_file(tmp_path, monkeypatch):
    import yaml as yaml_module

    path = _write(tmp_path, "whatsapp:\n  provider: console\n")

    def boom(*args, **kwargs):
        raise yaml_module.YAMLError("something odd")

    monkeypatch.setattr(yaml_module, "safe_load", boom)
    message = str(pytest.raises(ConfigError, load_settings, path).value)
    assert str(path) in message


def test_secrets_are_redacted_before_logging():
    payload = {
        "username": "me@example.com",
        "password": "hunter2",
        "meta": {"access_token": "abc", "phone_number_id": "123"},
        "items": [{"auth_token": "xyz"}],
    }
    assert redact(payload) == {
        "username": "me@example.com",
        "password": "***",
        "meta": {"access_token": "***", "phone_number_id": "123"},
        "items": [{"auth_token": "***"}],
    }
