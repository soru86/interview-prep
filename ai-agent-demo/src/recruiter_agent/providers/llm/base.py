from __future__ import annotations

from abc import ABC, abstractmethod

from recruiter_agent.models import DraftReply, JobDetails, MatchResult


class LLMClient(ABC):
    @abstractmethod
    async def extract_job_details(self, email_subject: str, email_body: str) -> JobDetails:
        raise NotImplementedError

    @abstractmethod
    async def match_resume(
        self, job: JobDetails, resume_text: str, match_threshold: int
    ) -> MatchResult:
        raise NotImplementedError

    @abstractmethod
    async def draft_reply(
        self,
        job: JobDetails,
        original_subject: str,
        original_body: str,
        recruiter_name: str,
        resume_text: str,
    ) -> DraftReply:
        raise NotImplementedError

    @abstractmethod
    async def is_recruiter_email(self, subject: str, body: str, sender_email: str) -> bool:
        raise NotImplementedError
