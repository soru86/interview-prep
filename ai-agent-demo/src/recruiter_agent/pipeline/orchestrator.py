from __future__ import annotations

from pathlib import Path

from recruiter_agent.config import Settings
from recruiter_agent.models import (
    MatchRecommendation,
    ProcessedEmailRecord,
    ProcessingStatus,
    TrackerRow,
)
from recruiter_agent.notifications import build_notifier
from recruiter_agent.notifications.whatsapp import Notifier
from recruiter_agent.pipeline.job_extractor import JobExtractor
from recruiter_agent.pipeline.recruiter_filter import RecruiterFilter
from recruiter_agent.pipeline.reply_drafter import ReplyDrafter
from recruiter_agent.pipeline.resume_matcher import ResumeMatcher
from recruiter_agent.providers.email.gmail import GmailProvider
from recruiter_agent.providers.llm.ollama import OllamaClient
from recruiter_agent.storage.excel_tracker import ExcelTracker
from recruiter_agent.storage.state_db import StateDB
from recruiter_agent.utils.logging import get_logger
from recruiter_agent.utils.resume_parser import load_resume_text

log = get_logger(__name__)


class Orchestrator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.llm = OllamaClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
        self.email_provider = GmailProvider(
            credentials_path=settings.gmail_credentials_path,
            token_path=settings.gmail_token_path,
        )
        self.state_db = StateDB(settings.state_db_path)
        self.tracker = ExcelTracker(settings.tracker_path, settings.excel_columns)
        self.filter = RecruiterFilter(settings, self.llm)
        self.extractor = JobExtractor(self.llm)
        self.matcher = ResumeMatcher(self.llm, settings)
        self.drafter = ReplyDrafter(self.llm, self.email_provider, settings.dry_run)
        self.notifier: Notifier = build_notifier(settings)

    async def initialize(self) -> None:
        await self.state_db.initialize()
        self.settings.resume_folder.mkdir(parents=True, exist_ok=True)

    async def run(self, max_emails: int = 50) -> dict:
        await self.initialize()
        resume_text, resume_path = load_resume_text(self.settings.resume_folder)

        emails = self.email_provider.fetch_labeled_emails(
            label_name=self.settings.gmail_recruiter_label,
            max_results=max_emails,
        )
        log.info("emails_fetched", count=len(emails), label=self.settings.gmail_recruiter_label)

        stats = {"processed": 0, "drafted": 0, "skipped": 0, "review": 0, "errors": 0}

        for email in emails:
            if await self.state_db.is_processed(email.message_id):
                log.info("email_already_processed", message_id=email.message_id)
                continue

            try:
                await self._process_email(email, resume_text, resume_path, stats)
            except Exception as exc:
                stats["errors"] += 1
                log.exception("email_processing_failed", message_id=email.message_id)
                await self.state_db.mark_processed(
                    ProcessedEmailRecord(
                        message_id=email.message_id,
                        status=ProcessingStatus.ERROR,
                        processed_at=StateDB.now(),
                        error_message=str(exc),
                    )
                )

        log.info("run_complete", **stats)
        return stats

    async def _process_email(
        self,
        email,
        resume_text: str,
        resume_path: Path,
        stats: dict,
    ) -> None:
        stats["processed"] += 1

        if not await self.filter.is_recruiter(email):
            await self._finalize(
                email,
                ProcessingStatus.SKIPPED,
                match_score=0,
                company="",
                role="",
                phone=None,
                stats=stats,
            )
            return

        job = await self.extractor.extract(email)
        match = await self.matcher.match(job, resume_text)

        if match.recommendation == MatchRecommendation.SKIP:
            await self._finalize(
                email,
                ProcessingStatus.SKIPPED,
                match_score=match.score,
                company=job.company,
                role=job.role_title,
                phone=job.recruiter_phone,
                stats=stats,
            )
            return

        if match.recommendation == MatchRecommendation.REVIEW:
            await self._finalize(
                email,
                ProcessingStatus.REVIEW,
                match_score=match.score,
                company=job.company,
                role=job.role_title,
                phone=job.recruiter_phone,
                stats=stats,
            )
            return

        draft = await self.drafter.create_draft(email, job, resume_text, resume_path)
        await self.notifier.send_draft_notification(
            recruiter_name=email.sender_name,
            role_title=job.role_title,
            company=job.company,
            match_score=match.score,
            subject=draft.subject,
        )
        await self._finalize(
            email,
            ProcessingStatus.DRAFTED,
            match_score=match.score,
            company=job.company,
            role=job.role_title,
            phone=job.recruiter_phone,
            stats=stats,
            reply_date=StateDB.now(),
        )

    async def _finalize(
        self,
        email,
        status: ProcessingStatus,
        match_score: int,
        company: str,
        role: str,
        phone: str | None,
        stats: dict,
        reply_date=None,
    ) -> None:
        if status == ProcessingStatus.DRAFTED:
            stats["drafted"] += 1
        elif status == ProcessingStatus.REVIEW:
            stats["review"] += 1
        else:
            stats["skipped"] += 1

        self.tracker.upsert_row(
            TrackerRow(
                recruiter_name=email.sender_name,
                contact_email=email.sender_email,
                contact_phone=phone,
                company=company or "Unknown",
                role_applied_for=role or "Unknown",
                match_score=match_score,
                date_of_first_reply=reply_date,
                email_subject=email.subject,
                status=status,
                message_id=email.message_id,
            )
        )
        await self.state_db.mark_processed(
            ProcessedEmailRecord(
                message_id=email.message_id,
                status=status,
                match_score=match_score,
                processed_at=StateDB.now(),
            )
        )

    async def status(self) -> dict:
        await self.initialize()
        processed = await self.state_db.count_processed()
        resume_exists = False
        if self.settings.resume_folder.exists():
            resume_exists = any(
                path.is_file() and not path.name.startswith(".")
                for path in self.settings.resume_folder.iterdir()
            )
        return {
            "processed_emails": processed,
            "tracker_path": str(self.settings.tracker_path),
            "resume_configured": resume_exists,
            "ollama_model": self.settings.ollama_model,
            "match_threshold": self.settings.match_threshold,
        }
