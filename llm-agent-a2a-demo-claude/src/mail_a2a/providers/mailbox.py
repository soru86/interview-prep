"""Mailbox readers.

Two implementations behind one interface:

* `ImapMailbox` — a real mailbox over IMAP, with plain LOGIN or XOAUTH2 (needed
  for outlook.com / Office 365, where Microsoft has disabled password LOGIN).
* `DemoMailbox` — reads `data/sample_emails.json`, so the whole two-agent
  pipeline can be demonstrated without handing the demo any credentials.
"""

from __future__ import annotations

import email
import imaplib
import json
import re
from abc import ABC, abstractmethod
from email.header import decode_header, make_header
from email.message import Message
from email.utils import parsedate_to_datetime, parseaddr
from pathlib import Path
from typing import Any

from mail_a2a.config import MailboxSettings
from mail_a2a.logging_setup import get_logger
from mail_a2a.models import EmailSummary

log = get_logger(__name__)

SNIPPET_CHARS = 600
_WHITESPACE = re.compile(r"\s+")


def _decode(raw: str | None) -> str:
    """Decode an RFC 2047 encoded header into plain text."""
    if not raw:
        return ""
    try:
        return str(make_header(decode_header(raw))).strip()
    except Exception:
        return raw.strip()


def _body_text(message: Message) -> str:
    """Best-effort plain-text body, preferring text/plain over stripped HTML."""
    plain: list[str] = []
    html: list[str] = []

    for part in message.walk() if message.is_multipart() else [message]:
        content_type = part.get_content_type()
        if part.get_content_maintype() == "multipart":
            continue
        if "attachment" in (part.get("Content-Disposition") or "").lower():
            continue
        if content_type not in ("text/plain", "text/html"):
            continue
        try:
            payload = part.get_payload(decode=True)
        except Exception:
            continue
        if not payload:
            continue
        charset = part.get_content_charset() or "utf-8"
        try:
            text = payload.decode(charset, errors="replace")
        except LookupError:
            text = payload.decode("utf-8", errors="replace")
        (plain if content_type == "text/plain" else html).append(text)

    text = "\n".join(plain) if plain else re.sub(r"<[^>]+>", " ", "\n".join(html))
    return _WHITESPACE.sub(" ", text).strip()


class Mailbox(ABC):
    """Everything the email MCP server needs from a mail source."""

    @abstractmethod
    def ping(self) -> dict[str, Any]:
        """Verify connectivity/credentials without fetching mail."""

    @abstractmethod
    def list_messages(self, max_results: int, unread_only: bool) -> list[EmailSummary]:
        """Newest-first message summaries."""

    @abstractmethod
    def mark_seen(self, uid: str) -> bool:
        """Flag a message as read. No-op sources return False."""

    def close(self) -> None:  # pragma: no cover - trivial
        return None


class DemoMailbox(Mailbox):
    """Fixture-backed mailbox for running the demo without credentials."""

    def __init__(self, sample_file: str | Path) -> None:
        self.path = Path(sample_file)

    def _load(self) -> list[EmailSummary]:
        if not self.path.is_file():
            log.error("demo_mailbox_missing_file", path=str(self.path))
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        items = raw.get("messages", raw) if isinstance(raw, dict) else raw
        return [EmailSummary.model_validate(item) for item in items]

    def ping(self) -> dict[str, Any]:
        messages = self._load()
        return {
            "ok": self.path.is_file(),
            "provider": "demo",
            "folder": str(self.path),
            "total": len(messages),
        }

    def list_messages(self, max_results: int, unread_only: bool) -> list[EmailSummary]:
        messages = self._load()
        if unread_only:
            messages = [item for item in messages if item.unread]
        selected = messages[:max_results]
        log.info(
            "mailbox_listed",
            provider="demo",
            returned=len(selected),
            unread_only=unread_only,
        )
        return selected

    def mark_seen(self, uid: str) -> bool:
        log.info("mailbox_mark_seen_skipped", provider="demo", uid=uid)
        return False


class ImapMailbox(Mailbox):
    """Real IMAP mailbox. Reads with BODY.PEEK so scanning never marks mail read."""

    def __init__(self, settings: MailboxSettings) -> None:
        self.settings = settings
        self._conn: imaplib.IMAP4 | None = None

    # -- connection ----------------------------------------------------------

    def connect(self) -> imaplib.IMAP4:
        if self._conn is not None:
            return self._conn

        cfg = self.settings
        log.info(
            "imap_connect",
            host=cfg.host,
            port=cfg.port,
            username=cfg.username,
            auth=cfg.auth,
            ssl=cfg.ssl,
        )
        conn: imaplib.IMAP4 = (
            imaplib.IMAP4_SSL(cfg.host, cfg.port) if cfg.ssl else imaplib.IMAP4(cfg.host, cfg.port)
        )

        if cfg.auth == "oauth2":
            from mail_a2a.providers.msal_auth import acquire_access_token

            token = acquire_access_token(cfg)
            conn.authenticate(
                "XOAUTH2",
                lambda _: f"user={cfg.username}\x01auth=Bearer {token}\x01\x01".encode(),
            )
        else:
            if not cfg.password:
                raise RuntimeError(
                    "mailbox.password is empty. Set it in config/config.yaml or "
                    "MAILBOX_PASSWORD, or switch mailbox.auth to oauth2."
                )
            conn.login(cfg.username, cfg.password)

        conn.select(cfg.folder, readonly=not cfg.mark_seen)
        self._conn = conn
        log.info("imap_connected", folder=cfg.folder, readonly=not cfg.mark_seen)
        return conn

    def close(self) -> None:
        if self._conn is None:
            return
        try:
            self._conn.close()
        except Exception:
            pass
        try:
            self._conn.logout()
        except Exception:
            pass
        self._conn = None
        log.info("imap_disconnected")

    # -- reads ---------------------------------------------------------------

    def ping(self) -> dict[str, Any]:
        conn = self.connect()
        status, data = conn.search(None, "ALL")
        total = len(data[0].split()) if status == "OK" and data and data[0] else 0
        return {
            "ok": status == "OK",
            "provider": "imap",
            "host": self.settings.host,
            "folder": self.settings.folder,
            "total": total,
        }

    def list_messages(self, max_results: int, unread_only: bool) -> list[EmailSummary]:
        conn = self.connect()
        criteria = "(UNSEEN)" if unread_only else "ALL"
        status, data = conn.uid("SEARCH", None, criteria)
        if status != "OK":
            raise RuntimeError(f"IMAP SEARCH failed: {status}")

        uids = data[0].split() if data and data[0] else []
        selected = list(reversed(uids))[:max_results]  # newest first
        log.info(
            "imap_search",
            criteria=criteria,
            matched=len(uids),
            fetching=len(selected),
        )

        summaries: list[EmailSummary] = []
        for raw_uid in selected:
            uid = raw_uid.decode()
            # PEEK leaves the \Seen flag alone; mark_seen is an explicit step.
            status, payload = conn.uid("FETCH", uid, "(BODY.PEEK[])")
            if status != "OK" or not payload or not isinstance(payload[0], tuple):
                log.warning("imap_fetch_failed", uid=uid, status=status)
                continue
            summaries.append(self._to_summary(uid, email.message_from_bytes(payload[0][1])))

        log.info("mailbox_listed", provider="imap", returned=len(summaries))
        return summaries

    @staticmethod
    def _to_summary(uid: str, message: Message) -> EmailSummary:
        from_header = _decode(message.get("From"))
        display_name, address = parseaddr(from_header)
        received_at = ""
        if raw_date := message.get("Date"):
            try:
                received_at = parsedate_to_datetime(raw_date).isoformat()
            except Exception:
                received_at = raw_date

        return EmailSummary(
            uid=uid,
            sender=from_header or address or "(unknown sender)",
            sender_email=address,
            subject=_decode(message.get("Subject")) or "(no subject)",
            received_at=received_at,
            snippet=_body_text(message)[:SNIPPET_CHARS],
            unread=True,
        )

    def mark_seen(self, uid: str) -> bool:
        if not self.settings.mark_seen:
            log.info("imap_mark_seen_disabled", uid=uid)
            return False
        conn = self.connect()
        status, _ = conn.uid("STORE", uid, "+FLAGS", "(\\Seen)")
        ok = status == "OK"
        log.info("imap_mark_seen", uid=uid, ok=ok)
        return ok


def build_mailbox(settings: MailboxSettings) -> Mailbox:
    if settings.provider == "demo":
        return DemoMailbox(settings.sample_file)
    return ImapMailbox(settings)
