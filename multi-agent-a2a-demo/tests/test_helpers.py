from a2a_mail_notify.a2a_support import parse_json_payload
from a2a_mail_notify.logging import sanitize_log_data


def test_parse_json_payload_embedded():
    text = 'please handle this {"sender": "Ada", "subject": "Hi", "priority": true}'
    data = parse_json_payload(text)
    assert data["sender"] == "Ada"
    assert data["priority"] is True


def test_parse_json_payload_empty():
    assert parse_json_payload("check mailbox") == {}


def test_sanitize_redacts_secrets():
    data = sanitize_log_data(
        {"username": "ada", "password": "secret", "meta": {"access_token": "abc"}}
    )
    assert data["username"] == "ada"
    assert data["password"] == "***"
    assert data["meta"]["access_token"] == "***"


def test_prefer_json_text_from_a2a_noise():
    from a2a_mail_notify.a2a_support import _prefer_json_text

    result = _prefer_json_text(["Working...", '{"notified": 1}', "Completed"])
    assert result == '{"notified": 1}'
