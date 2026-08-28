from __future__ import annotations

import base64
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from recruiter_agent.models import EmailMessage
from recruiter_agent.utils.logging import get_logger

log = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
]


class EmailProvider(ABC):
    @abstractmethod
    def fetch_labeled_emails(self, label_name: str, max_results: int = 50) -> list[EmailMessage]:
        raise NotImplementedError

    @abstractmethod
    def create_draft(
        self,
        to_email: str,
        subject: str,
        body: str,
        thread_id: str,
        attachment_path: Optional[Path] = None,
    ) -> str:
        raise NotImplementedError


class GmailProvider(EmailProvider):
    def __init__(self, credentials_path: Path, token_path: Path) -> None:
        self.credentials_path = credentials_path
        self.token_path = token_path
        self._service = None

    def _get_service(self):
        if self._service is not None:
            return self._service

        creds = None
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Gmail credentials not found at {self.credentials_path}. "
                        "Download OAuth credentials from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            self.token_path.write_text(creds.to_json())

        self._service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        return self._service

    def _get_label_id(self, label_name: str) -> str:
        service = self._get_service()
        labels = service.users().labels().list(userId="me").execute().get("labels", [])
        for label in labels:
            if label["name"].lower() == label_name.lower():
                return label["id"]
        raise ValueError(
            f"Gmail label '{label_name}' not found. Create it in Gmail and apply to recruiter emails."
        )

    def fetch_labeled_emails(self, label_name: str, max_results: int = 50) -> list[EmailMessage]:
        service = self._get_service()
        label_id = self._get_label_id(label_name)
        query = f"label:{label_name}"

        try:
            listing = (
                service.users()
                .messages()
                .list(userId="me", labelIds=[label_id], q=query, maxResults=max_results)
                .execute()
            )
        except HttpError as exc:
            log.error("gmail_list_failed", error=str(exc))
            raise

        messages: list[EmailMessage] = []
        for item in listing.get("messages", []):
            full = (
                service.users()
                .messages()
                .get(userId="me", id=item["id"], format="full")
                .execute()
            )
            parsed = self._parse_message(full)
            if parsed:
                messages.append(parsed)
        return messages

    def create_draft(
        self,
        to_email: str,
        subject: str,
        body: str,
        thread_id: str,
        attachment_path: Optional[Path] = None,
    ) -> str:
        service = self._get_service()
        message = self._build_mime_message(to_email, subject, body, attachment_path)
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        draft_body: dict = {"message": {"raw": raw, "threadId": thread_id}}
        draft = service.users().drafts().create(userId="me", body=draft_body).execute()
        draft_id = draft.get("id", "")
        log.info("gmail_draft_created", draft_id=draft_id, to=to_email, subject=subject)
        return draft_id

    def _build_mime_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment_path: Optional[Path],
    ) -> MIMEMultipart:
        from email.mime.application import MIMEApplication

        message = MIMEMultipart()
        message["to"] = to_email
        message["subject"] = subject
        message.attach(MIMEText(body, "plain"))

        if attachment_path and attachment_path.exists():
            with attachment_path.open("rb") as handle:
                part = MIMEApplication(handle.read(), Name=attachment_path.name)
            part["Content-Disposition"] = f'attachment; filename="{attachment_path.name}"'
            message.attach(part)
        return message

    def _parse_message(self, payload: dict) -> Optional[EmailMessage]:
        headers = {
            header["name"].lower(): header["value"]
            for header in payload.get("payload", {}).get("headers", [])
        }
        subject = headers.get("subject", "(no subject)")
        from_header = headers.get("from", "")
        sender_name, sender_email = _parse_from_header(from_header)
        body_text = _extract_body(payload.get("payload", {}))
        internal_date = int(payload.get("internalDate", "0")) / 1000
        received_at = datetime.fromtimestamp(internal_date, tz=timezone.utc)

        return EmailMessage(
            message_id=payload["id"],
            thread_id=payload.get("threadId", ""),
            subject=subject,
            sender_name=sender_name,
            sender_email=sender_email,
            body_text=body_text,
            received_at=received_at,
            labels=payload.get("labelIds", []),
        )


def _parse_from_header(from_header: str) -> tuple[str, str]:
    match = re.match(r'(?:"?([^"]*)"?\s)?<?([^>]+@[^>]+)>?', from_header.strip())
    if match:
        name = (match.group(1) or "").strip()
        email = match.group(2).strip()
        return name or email.split("@")[0], email
    return from_header, from_header


def _extract_body(payload: dict) -> str:
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")

    if mime_type == "text/plain" and body_data:
        return base64.urlsafe_b64decode(body_data.encode("utf-8")).decode(
            "utf-8", errors="replace"
        )

    parts = payload.get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data")
            if data:
                return base64.urlsafe_b64decode(data.encode("utf-8")).decode(
                    "utf-8", errors="replace"
                )

    for part in parts:
        nested = _extract_body(part)
        if nested:
            return nested

    if body_data:
        return base64.urlsafe_b64decode(body_data.encode("utf-8")).decode(
            "utf-8", errors="replace"
        )
    return ""
