from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MatchRecommendation(str, Enum):
    APPLY = "APPLY"
    REVIEW = "REVIEW"
    SKIP = "SKIP"


class ProcessingStatus(str, Enum):
    DRAFTED = "drafted"
    SKIPPED = "skipped"
    REVIEW = "review"
    ERROR = "error"


class EmailMessage(BaseModel):
    message_id: str
    thread_id: str
    subject: str
    sender_name: str
    sender_email: str
    body_text: str
    received_at: datetime
    labels: list[str] = Field(default_factory=list)


class JobDetails(BaseModel):
    role_title: str
    company: str
    location: Optional[str] = None
    remote: Optional[bool] = None
    required_skills: list[str] = Field(default_factory=list)
    experience_years: Optional[str] = None
    salary: Optional[str] = None
    application_instructions: list[str] = Field(default_factory=list)
    recruiter_phone: Optional[str] = None
    summary: str = ""


class MatchResult(BaseModel):
    score: int = Field(ge=0, le=100)
    matched_skills: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    recommendation: MatchRecommendation
    reasoning: str = ""


class DraftReply(BaseModel):
    subject: str
    body: str


class TrackerRow(BaseModel):
    recruiter_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    company: str
    role_applied_for: str
    match_score: int
    date_of_first_reply: Optional[datetime] = None
    email_subject: str
    status: ProcessingStatus
    message_id: str


class ProcessedEmailRecord(BaseModel):
    message_id: str
    status: ProcessingStatus
    match_score: Optional[int] = None
    processed_at: datetime
    error_message: Optional[str] = None
