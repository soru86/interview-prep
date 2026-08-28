from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EmailSummary(BaseModel):
    uid: str
    message_id: str
    sender: str
    subject: str
    date: str = ""


class EmailMessage(BaseModel):
    uid: str
    message_id: str
    sender: str
    subject: str
    date: str = ""
    body: str = ""


class EmailAlert(BaseModel):
    sender: str
    subject: str
    priority: bool = False
    snippet: str = ""
    message_id: str = ""
    uid: str = ""


class NotifyResult(BaseModel):
    ok: bool
    provider: str = ""
    message_id: str = ""
    dry_run: bool = False
    body: str = ""
    error: Optional[str] = None


class MailboxRunStats(BaseModel):
    listed: int = 0
    skipped_processed: int = 0
    notified: int = 0
    errors: int = 0
    alerts: list[EmailAlert] = Field(default_factory=list)


class ProcessedEmailRecord(BaseModel):
    message_id: str
    status: str
    processed_at: datetime
    error_message: Optional[str] = None
