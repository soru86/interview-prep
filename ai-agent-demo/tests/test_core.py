from __future__ import annotations

import json

import pytest

from recruiter_agent.models import JobDetails, MatchRecommendation, MatchResult
from recruiter_agent.pipeline.recruiter_filter import RecruiterFilter
from recruiter_agent.storage.excel_tracker import ExcelTracker
from recruiter_agent.utils.resume_parser import extract_json_object


class FakeLLM:
    async def is_recruiter_email(self, subject: str, body: str, sender_email: str) -> bool:
        return "recruiter" in subject.lower()


def test_extract_json_object_from_markdown_fence():
    raw = 'Some text\n```json\n{"score": 85, "recommendation": "APPLY"}\n```'
    data = extract_json_object(raw)
    assert data["score"] == 85


def test_extract_json_object_strips_thinking_block():
    think_open = "<" + "think" + ">"
    think_close = "<" + "/think" + ">"
    raw = f"{think_open}long reasoning{think_close}\n{{\"is_recruiter\": true}}"
    data = extract_json_object(raw)
    assert data["is_recruiter"] is True


def test_recruiter_filter_heuristics(settings):
    settings.recruiter_keywords = ["hiring"]
    filt = RecruiterFilter(settings, FakeLLM())
    from recruiter_agent.models import EmailMessage
    from datetime import datetime, timezone

    email = EmailMessage(
        message_id="1",
        thread_id="t1",
        subject="We are hiring engineers",
        sender_name="Jane",
        sender_email="jane@agency.com",
        body_text="Role details...",
        received_at=datetime.now(timezone.utc),
    )
    assert filt.passes_heuristics(email) is True


def test_excel_tracker_upsert(tmp_path):
    tracker_path = tmp_path / "tracker.xlsx"
    tracker = ExcelTracker(tracker_path)
    from recruiter_agent.models import ProcessingStatus, TrackerRow
    from datetime import datetime, timezone

    row = TrackerRow(
        recruiter_name="Jane Doe",
        contact_email="jane@recruit.com",
        contact_phone="+123",
        company="Acme",
        role_applied_for="Backend Engineer",
        match_score=82,
        date_of_first_reply=datetime(2026, 1, 1, tzinfo=timezone.utc),
        email_subject="Backend role",
        status=ProcessingStatus.DRAFTED,
        message_id="msg-001",
    )
    tracker.upsert_row(row)
    tracker.upsert_row(row)
    assert tracker_path.exists()


def test_match_result_validation():
    result = MatchResult(
        score=75,
        matched_skills=["Python"],
        gaps=["Kubernetes"],
        recommendation=MatchRecommendation.APPLY,
        reasoning="Strong fit",
    )
    assert result.score == 75


def test_job_details_from_json():
    payload = {
        "role_title": "Data Engineer",
        "company": "Contoso",
        "required_skills": ["Python", "SQL"],
        "summary": "Great role",
    }
    job = JobDetails.model_validate(payload)
    assert job.role_title == "Data Engineer"
