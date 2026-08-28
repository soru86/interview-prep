from __future__ import annotations

from recruiter_agent.config import Settings
from recruiter_agent.models import EmailMessage
from recruiter_agent.providers.llm.base import LLMClient
from recruiter_agent.utils.logging import get_logger

log = get_logger(__name__)


class RecruiterFilter:
    def __init__(self, settings: Settings, llm: LLMClient) -> None:
        self.settings = settings
        self.llm = llm

    def passes_heuristics(self, email: EmailMessage) -> bool:
        haystack = f"{email.subject} {email.body_text}".lower()
        sender = email.sender_email.lower()

        if any(keyword in haystack for keyword in self.settings.recruiter_keywords):
            return True
        if any(domain in sender for domain in self.settings.recruiter_domains):
            return True
        return False

    async def is_recruiter(self, email: EmailMessage) -> bool:
        if self.passes_heuristics(email):
            return True
        return await self.llm.is_recruiter_email(
            email.subject, email.body_text, email.sender_email
        )
