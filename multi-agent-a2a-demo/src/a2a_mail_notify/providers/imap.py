from __future__ import annotations

import email
import imaplib
from collections.abc import Callable
from email.header import decode_header, make_header
from email.message import Message
from email.utils import parseaddr

from a2a_mail_notify.logging import get_logger
from a2a_mail_notify.models import EmailMessage, EmailSummary
from a2a_mail_notify.providers.microsoft_oauth import xoauth2_payload

log = get_logger(__name__)


def _decode_header_value(raw: str | None) -> str:
    if not raw:
        return ""
    try:
        return str(make_header(decode_header(raw)))
    except Exception:
        return raw


def _body_from_message(message: Message) -> str:
    if message.is_multipart():
        parts: list[str] = []
        for part in message.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition") or "")
            if content_type == "text/plain" and "attachment" not in disposition.lower():
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    parts.append(payload.decode(charset, errors="replace"))
        if parts:
            return "\n".join(parts).strip()
        return ""
    payload = message.get_payload(decode=True)
    if not payload:
        return str(message.get_payload() or "")
    charset = message.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace").strip()


class ImapProvider:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        folder: str = "INBOX",
        ssl: bool = True,
        auth: str = "password",
        token_provider: Callable[[], str] | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.folder = folder
        self.ssl = ssl
        self.auth = auth
        self._token_provider = token_provider
        self._client: imaplib.IMAP4 | imaplib.IMAP4_SSL | None = None

    def connect(self) -> None:
        log.info(
            "imap_connect",
            host=self.host,
            port=self.port,
            username=self.username,
            folder=self.folder,
            ssl=self.ssl,
            auth=self.auth,
        )
        client: imaplib.IMAP4 | imaplib.IMAP4_SSL
        if self.ssl:
            client = imaplib.IMAP4_SSL(self.host, self.port)
        else:
            client = imaplib.IMAP4(self.host, self.port)
        try:
            if self.auth == "oauth2":
                if self._token_provider is None:
                    raise RuntimeError("OAuth2 IMAP requires a token provider.")
                token = self._token_provider()
                client.authenticate("XOAUTH2", lambda _challenge: xoauth2_payload(self.username, token))
            else:
                self._login_with_password(client)
        except imaplib.IMAP4.error as exc:
            raise RuntimeError(format_imap_error(exc, host=self.host, auth=self.auth)) from exc
        status, _ = client.select(self.folder, readonly=False)
        if status != "OK":
            raise RuntimeError(f"Unable to select IMAP folder {self.folder!r}")
        self._client = client
        log.info("imap_connected", folder=self.folder, auth=self.auth)

    def _login_with_password(self, client: imaplib.IMAP4) -> None:
        try:
            client.login(self.username, self.password)
            return
        except imaplib.IMAP4.error:
            log.info("imap_login_retry_plain", host=self.host)
        client.authenticate(
            "PLAIN",
            lambda _challenge: f"\0{self.username}\0{self.password}".encode(),
        )

    @property
    def client(self) -> imaplib.IMAP4:
        if self._client is None:
            raise RuntimeError("IMAP client is not connected.")
        return self._client

    def close(self) -> None:
        if self._client is None:
            return
        try:
            self._client.close()
        except Exception:
            pass
        try:
            self._client.logout()
        except Exception:
            pass
        self._client = None
        log.info("imap_closed")

    def ping(self) -> dict:
        typ, data = self.client.noop()
        banner = ""
        if data and data[0]:
            banner = data[0].decode(errors="replace") if isinstance(data[0], bytes) else str(data[0])
        return {"ok": typ == "OK", "noop": banner, "host": self.host, "folder": self.folder}

    def list_unread(self, max_results: int = 20, unread_only: bool = True) -> list[EmailSummary]:
        criteria = "UNSEEN" if unread_only else "ALL"
        typ, data = self.client.uid("search", None, criteria)
        if typ != "OK":
            raise RuntimeError(f"IMAP search failed: {typ}")
        uids = (data[0] or b"").split()
        selected = uids[-max_results:] if max_results else uids
        log.info(
            "imap_list",
            criteria=criteria,
            total=len(uids),
            returning=len(selected),
        )
        summaries: list[EmailSummary] = []
        for uid in selected:
            uid_str = uid.decode() if isinstance(uid, bytes) else str(uid)
            summaries.append(self._fetch_headers(uid_str))
        return summaries

    def fetch_message(self, uid: str) -> EmailMessage:
        typ, data = self.client.uid("fetch", uid, "(RFC822)")
        if typ != "OK" or not data or data[0] is None:
            raise RuntimeError(f"IMAP fetch failed for uid={uid}")
        raw = data[0][1] if isinstance(data[0], tuple) else data[0]
        message = email.message_from_bytes(raw)
        sender_name, sender_email = parseaddr(_decode_header_value(message.get("From")))
        sender = f"{sender_name} <{sender_email}>".strip() if sender_name else sender_email
        subject = _decode_header_value(message.get("Subject"))
        message_id = (message.get("Message-ID") or uid).strip()
        date = _decode_header_value(message.get("Date"))
        body = _body_from_message(message)
        log.info("imap_fetch", uid=uid, message_id=message_id, subject=subject[:120])
        return EmailMessage(
            uid=uid,
            message_id=message_id,
            sender=sender or sender_email,
            subject=subject,
            date=date,
            body=body,
        )

    def mark_seen(self, uid: str) -> bool:
        typ, _ = self.client.uid("store", uid, "+FLAGS", "(\\Seen)")
        ok = typ == "OK"
        log.info("imap_mark_seen", uid=uid, ok=ok)
        return ok

    def _fetch_headers(self, uid: str) -> EmailSummary:
        typ, data = self.client.uid(
            "fetch",
            uid,
            "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE MESSAGE-ID)])",
        )
        if typ != "OK" or not data:
            return EmailSummary(uid=uid, message_id=uid, sender="", subject="")
        raw = b""
        for item in data:
            if isinstance(item, tuple) and len(item) >= 2 and isinstance(item[1], bytes):
                raw = item[1]
                break
        message = email.message_from_bytes(raw) if raw else email.message_from_string("")
        sender_name, sender_email = parseaddr(_decode_header_value(message.get("From")))
        sender = f"{sender_name} <{sender_email}>".strip() if sender_name else sender_email
        subject = _decode_header_value(message.get("Subject"))
        message_id = (message.get("Message-ID") or uid).strip()
        date = _decode_header_value(message.get("Date"))
        return EmailSummary(
            uid=uid,
            message_id=message_id,
            sender=sender or sender_email,
            subject=subject,
            date=date,
        )


def format_imap_error(exc: BaseException, *, host: str = "", auth: str = "password") -> str:
    raw = exc.args[0] if getattr(exc, "args", None) else exc
    if isinstance(raw, bytes):
        text = raw.decode(errors="replace")
    else:
        text = str(raw)
    outlook = any(token in host.lower() for token in ("outlook", "office365", "hotmail", "live.com"))
    if outlook and auth != "oauth2" and ("AUTHENTICATE failed" in text or "LOGIN failed" in text):
        return (
            f"{text}. Microsoft blocked username/password IMAP for Outlook.com. "
            "Set mailbox.auth: oauth2 and mailbox.oauth_client_id, then run: a2a-mail-notify login"
        )
    return text


def build_imap_provider(settings, *, allow_interactive_login: bool = False) -> ImapProvider:
    mailbox = settings.mailbox
    token_provider = None
    if mailbox.auth == "oauth2":
        from a2a_mail_notify.providers.microsoft_oauth import MicrosoftImapAuth

        auth_client = MicrosoftImapAuth(
            client_id=mailbox.oauth_client_id,
            tenant=mailbox.oauth_tenant,
            username=mailbox.username,
            cache_path=mailbox.oauth_token_cache,
        )
        if allow_interactive_login:
            token_provider = auth_client.acquire_device_code
        else:
            token_provider = auth_client.acquire_silent
    return ImapProvider(
        host=mailbox.host,
        port=mailbox.port,
        username=mailbox.username,
        password=mailbox.password,
        folder=mailbox.folder,
        ssl=mailbox.ssl,
        auth=mailbox.auth,
        token_provider=token_provider,
    )
