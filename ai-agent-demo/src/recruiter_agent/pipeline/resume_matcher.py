from __future__ import annotations

from recruiter_agent.config import Settings
from recruiter_agent.models import JobDetails, MatchRecommendation, MatchResult
from recruiter_agent.providers.llm.base import LLMClient
from recruiter_agent.utils.logging import get_logger

log = get_logger(__name__)


class ResumeMatcher:
    def __init__(self, llm: LLMClient, settings: Settings) -> None:
        self.llm = llm
        self.settings = settings

    async def match(self, job: JobDetails, resume_text: str) -> MatchResult:
        result = await self.llm.match_resume(
            job, resume_text, self.settings.match_threshold
        )
        if result.score >= self.settings.match_threshold:
            if result.recommendation == MatchRecommendation.SKIP:
                result.recommendation = MatchRecommendation.REVIEW
        log.info(
            "resume_matched",
            role=job.role_title,
            score=result.score,
            recommendation=result.recommendation.value,
        )
        return result
