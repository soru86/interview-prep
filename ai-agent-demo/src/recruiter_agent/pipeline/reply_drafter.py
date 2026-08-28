from __future__ import annotations

from pathlib import Path

from recruiter_agent.models import DraftReply, EmailMessage, JobDetails
from recruiter_agent.providers.email.gmail import GmailProvider
from recruiter_agent.providers.llm.base import LLMClient
from recruiter_agent.utils.logging import get_logger

log = get_logger(__name__)


class ReplyDrafter:
    def __init__(
        self,
        llm: LLMClient,
        email_provider: GmailProvider,
        dry_run: bool = False,
    ) -> None:
        self.llm = llm
        self.email_provider = email_provider
        self.dry_run = dry_run

    async def create_draft(
        self,
        email: EmailMessage,
        job: JobDetails,
        resume_text: str,
        resume_path: Path,
    ) -> DraftReply:
        draft = await self.llm.draft_reply(
            job=job,
            original_subject=email.subject,
            original_body=email.body_text,
            recruiter_name=email.sender_name,
            resume_text=resume_text,
        )

        if self.dry_run:
            log.info(
                "draft_skipped_dry_run",
                to=email.sender_email,
                subject=draft.subject,
            )
            return draft

        self.email_provider.create_draft(
            to_email=email.sender_email,
            subject=draft.subject,
            body=draft.body,
            thread_id=email.thread_id,
            attachment_path=resume_path,
        )
        return draft
