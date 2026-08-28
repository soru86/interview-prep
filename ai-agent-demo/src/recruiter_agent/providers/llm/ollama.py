from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from recruiter_agent.models import DraftReply, JobDetails, MatchRecommendation, MatchResult
from recruiter_agent.providers.llm.base import LLMClient
from recruiter_agent.utils.logging import get_logger
from recruiter_agent.utils.resume_parser import extract_json_object

log = get_logger(__name__)


class OllamaClient(LLMClient):
    def __init__(self, base_url: str, model: str, timeout_seconds: int = 300) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=20))
    async def _chat(self, system: str, user: str, temperature: float = 0.2) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": temperature},
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "")
            if not content:
                raise ValueError("Empty response from Ollama.")
            return content

    async def extract_job_details(self, email_subject: str, email_body: str) -> JobDetails:
        system = (
            "You extract structured job information from recruiter emails. "
            "Respond with ONLY valid JSON, no markdown or explanation."
        )
        user = f"""Extract job details from this email.

Subject: {email_subject}

Body:
{email_body[:8000]}

Return JSON with keys:
role_title, company, location, remote (boolean or null), required_skills (array),
experience_years, salary, application_instructions (array), recruiter_phone, summary"""
        raw = await self._chat(system, user)
        data = extract_json_object(raw)
        return JobDetails.model_validate(data)

    async def match_resume(
        self, job: JobDetails, resume_text: str, match_threshold: int
    ) -> MatchResult:
        system = (
            "You are a career matching assistant. Compare a job description with a resume. "
            "Respond with ONLY valid JSON."
        )
        user = f"""Job:
{job.model_dump_json()}

Resume:
{resume_text[:12000]}

Minimum acceptable score threshold: {match_threshold}

Return JSON with keys:
score (0-100 integer),
matched_skills (array of strings),
gaps (array of strings),
recommendation (one of APPLY, REVIEW, SKIP),
reasoning (short string)

Use APPLY if score >= {match_threshold} and candidate is a strong fit.
Use REVIEW if borderline. Use SKIP if poor fit."""
        raw = await self._chat(system, user)
        data = extract_json_object(raw)
        result = MatchResult.model_validate(data)
        if result.score >= match_threshold and result.recommendation == MatchRecommendation.SKIP:
            result.recommendation = MatchRecommendation.REVIEW
        return result

    async def draft_reply(
        self,
        job: JobDetails,
        original_subject: str,
        original_body: str,
        recruiter_name: str,
        resume_text: str,
    ) -> DraftReply:
        system = (
            "You write concise, professional email replies to recruiters. "
            "Address any requested details (availability, notice period, salary expectations, "
            "work authorization) using plausible placeholders where personal facts are unknown: "
            "[Your Notice Period], [Your Expected Salary], [Your Availability]. "
            "Respond with ONLY valid JSON."
        )
        user = f"""Draft a reply to this recruiter email.

Recruiter name: {recruiter_name}
Original subject: {original_subject}
Original body:
{original_body[:6000]}

Job details:
{job.model_dump_json()}

Resume summary (for context):
{resume_text[:4000]}

Return JSON with keys: subject, body
The body should be plain text, professional, and mention that your CV is attached."""
        raw = await self._chat(system, user, temperature=0.4)
        data = extract_json_object(raw)
        return DraftReply.model_validate(data)

    async def is_recruiter_email(self, subject: str, body: str, sender_email: str) -> bool:
        system = (
            "Classify whether an email is from a recruiter about a job opportunity. "
            "Respond with ONLY valid JSON: {\"is_recruiter\": true/false}"
        )
        user = f"""Sender: {sender_email}
Subject: {subject}
Body excerpt:
{body[:3000]}"""
        raw = await self._chat(system, user, temperature=0.0)
        data = extract_json_object(raw)
        return bool(data.get("is_recruiter", False))
