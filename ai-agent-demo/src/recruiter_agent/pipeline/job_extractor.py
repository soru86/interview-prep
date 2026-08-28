from __future__ import annotations

from recruiter_agent.models import EmailMessage, JobDetails
from recruiter_agent.providers.llm.base import LLMClient
from recruiter_agent.utils.logging import get_logger

log = get_logger(__name__)


class JobExtractor:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def extract(self, email: EmailMessage) -> JobDetails:
        job = await self.llm.extract_job_details(email.subject, email.body_text)
        log.info(
            "job_extracted",
            message_id=email.message_id,
            role=job.role_title,
            company=job.company,
        )
        return job
