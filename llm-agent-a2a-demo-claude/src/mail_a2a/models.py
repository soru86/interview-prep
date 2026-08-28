"""Payloads exchanged between the two agents and their MCP tools.

Everything crossing an A2A or MCP boundary is one of these models serialized to
JSON, so both ends validate the same shape.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EmailSummary(BaseModel):
    """One mailbox message as returned by the email MCP server."""

    uid: str
    sender: str = ""
    sender_email: str = ""
    subject: str = "(no subject)"
    received_at: str = ""
    snippet: str = ""
    unread: bool = True


class ScanRequest(BaseModel):
    """Runner -> mailbox agent (A2A)."""

    action: str = "scan_and_notify"
    max_emails: int = 10
    unread_only: bool = True


class NotifyRequest(BaseModel):
    """Mailbox agent -> WhatsApp agent (A2A).

    `priority` is decided by the mailbox agent using the configured keywords, so
    the notifier never has to re-derive it.
    """

    uid: str
    sender: str
    subject: str
    priority: bool = False
    matched_keywords: list[str] = Field(default_factory=list)
    received_at: str = ""
    snippet: str = ""
    summary: str = ""


class NotifyResult(BaseModel):
    """WhatsApp agent -> mailbox agent (A2A)."""

    uid: str = ""
    ok: bool = False
    provider: str = ""
    to: str = ""
    message_id: str = ""
    text: str = ""
    error: str = ""


class ScanResult(BaseModel):
    """Mailbox agent -> runner (A2A)."""

    scanned: int = 0
    new: int = 0
    notified: int = 0
    failed: int = 0
    priority: int = 0
    results: list[NotifyResult] = Field(default_factory=list)
    error: str = ""

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump()
