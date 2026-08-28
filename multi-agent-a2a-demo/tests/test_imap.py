from email.message import EmailMessage as StdEmail

import imaplib

from a2a_mail_notify.providers.imap import ImapProvider, _body_from_message, _decode_header_value, format_imap_error
from a2a_mail_notify.providers.microsoft_oauth import xoauth2_payload
from a2a_mail_notify.runner import port_busy_message, strip_inline_comment_args


def test_decode_encoded_subject():
    assert "Hello" in _decode_header_value("Hello")


def test_plain_body_extraction():
    message = StdEmail()
    message["From"] = "Ada <ada@example.com>"
    message["Subject"] = "Hi"
    message.set_content("Plain body here")
    # EmailMessage.set_content makes multipart/alternative in newer Python; handle both.
    body = _body_from_message(message)
    assert "Plain body here" in body


def test_connect_requires_client():
    provider = ImapProvider("imap.example.com", 993, "u", "p")
    try:
        _ = provider.client
        raise AssertionError("expected RuntimeError")
    except RuntimeError:
        pass


def test_msal_scopes_are_not_reserved():
    from a2a_mail_notify.providers.microsoft_oauth import IMAP_SCOPES

    reserved = {"profile", "openid", "offline_access"}
    assert reserved.isdisjoint(IMAP_SCOPES)
    assert "https://outlook.office.com/IMAP.AccessAsUser.All" in IMAP_SCOPES


def test_xoauth2_payload():
    raw = xoauth2_payload("ada@outlook.com", "tok")
    assert raw.startswith(b"user=ada@outlook.com")
    assert b"Bearer tok" in raw


def test_outlook_auth_error_explains_oauth():
    err = format_imap_error(
        imaplib.IMAP4.error(b"AUTHENTICATE failed."),
        host="outlook.office365.com",
        auth="password",
    )
    assert "AUTHENTICATE failed" in err
    assert "a2a-mail-notify login" in err


def test_strip_hash_comments_from_cli():
    assert strip_inline_comment_args(["run", "#", "one", "check"]) == ["run"]
    assert strip_inline_comment_args(["run", "--once"]) == ["run", "--once"]


def test_port_busy_message_mentions_lsof():
    message = port_busy_message("WhatsApp agent", "127.0.0.1", 9002)
    assert "9002" in message
    assert "already in use" in message
    assert "lsof" in message
