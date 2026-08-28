"""Agent 1 — the mailbox reader.

Reads the mailbox through the `email-mcp` tool server, decides which messages
are top priority, asks DeepSeek R1 for a one-line summary of each, and then
hands every new message to agent 2 over A2A.

Priority is decided here by exact keyword matching (see `priority.py`); the model
is asked for its own opinion purely so the two can be compared in the logs.
"""

from __future__ import annotations

import json

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentSkill
from starlette.applications import Starlette

from mail_a2a import priority
from mail_a2a.a2a_common import (
    build_agent_card,
    build_app,
    complete_with_json,
    open_a2a_client,
    parse_json,
    request_text,
    send_json,
)
from mail_a2a.config import Settings
from mail_a2a.llm import OllamaClient
from mail_a2a.logging_setup import get_logger
from mail_a2a.mcp_client import open_email_mcp
from mail_a2a.models import EmailSummary, NotifyRequest, NotifyResult, ScanRequest, ScanResult
from mail_a2a.state import SeenStore

log = get_logger(__name__)

AGENT_NAME = "mailbox-reader-agent"

SUMMARY_SYSTEM_PROMPT = (
    "You triage email. Reply with a single JSON object and nothing else, using "
    'exactly these keys: {"summary": "<max 18 words>", "job_related": true|false}. '
    "No markdown, no code fences, no commentary."
)


def _summary_prompt(message: EmailSummary) -> str:
    return (
        f"From: {message.sender}\n"
        f"Subject: {message.subject}\n"
        f"Body: {message.snippet[:500] or '(empty)'}\n\n"
        "Summarize this email and say whether it is about a job, opening, "
        "position or career opportunity. Answer with the JSON object."
    )


class MailboxAgentExecutor(AgentExecutor):
    """A2A skill: `scan_and_notify`."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.llm = OllamaClient(settings.ollama, agent=AGENT_NAME)
        self.seen = SeenStore(settings.state_file)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        raw = request_text(context)
        log.info("a2a_received", agent=AGENT_NAME, skill="scan_and_notify", payload_chars=len(raw))

        payload = parse_json(raw)
        request = ScanRequest.model_validate(
            {"max_emails": self.settings.max_emails, **payload}
            if payload
            else {"max_emails": self.settings.max_emails}
        )

        try:
            result = await self._scan_and_notify(request)
        except Exception as exc:
            log.exception("scan_failed", agent=AGENT_NAME, error=str(exc))
            result = ScanResult(error=str(exc))

        await complete_with_json(context, event_queue, result.as_dict())

    # -- pipeline ------------------------------------------------------------

    async def _scan_and_notify(self, request: ScanRequest) -> ScanResult:
        messages = await self._read_mailbox(request)
        result = ScanResult(scanned=len(messages))

        fresh = [item for item in messages if not self.seen.has(item.uid)]
        result.new = len(fresh)
        log.info(
            "mailbox_scan",
            agent=AGENT_NAME,
            scanned=result.scanned,
            already_notified=result.scanned - result.new,
            to_notify=result.new,
        )
        if not fresh:
            return result

        peer_url = self.settings.agents.whatsapp.url
        timeout = self.settings.ollama.timeout_seconds + 60

        async with open_a2a_client(peer_url, timeout_seconds=timeout) as client:
            for message in fresh:
                notify_request = await self._build_notification(message)
                if notify_request.priority:
                    result.priority += 1

                reply = await send_json(
                    client,
                    notify_request.model_dump(),
                    peer=peer_url,
                    skill="notify_whatsapp",
                )
                notify_result = NotifyResult.model_validate(
                    {**reply, "uid": reply.get("uid") or message.uid}
                )
                result.results.append(notify_result)

                if notify_result.ok:
                    result.notified += 1
                    self.seen.add(message.uid)
                    await self._mark_seen(message.uid)
                else:
                    result.failed += 1
                    log.error(
                        "notify_rejected",
                        agent=AGENT_NAME,
                        uid=message.uid,
                        error=notify_result.error or "no result returned by notifier",
                    )

        self.seen.save()
        log.info(
            "mailbox_scan_complete",
            agent=AGENT_NAME,
            notified=result.notified,
            failed=result.failed,
            priority=result.priority,
        )
        return result

    async def _read_mailbox(self, request: ScanRequest) -> list[EmailSummary]:
        async with open_email_mcp() as mcp:
            payload = await mcp.call(
                "list_messages",
                {"max_results": request.max_emails, "unread_only": request.unread_only},
            )
        if isinstance(payload, str):
            payload = parse_json(payload)
        return [EmailSummary.model_validate(item) for item in (payload or {}).get("messages", [])]

    async def _mark_seen(self, uid: str) -> None:
        if not self.settings.mailbox.mark_seen:
            return
        try:
            async with open_email_mcp() as mcp:
                await mcp.call("mark_seen", {"uid": uid})
        except Exception as exc:  # a failed flag update must not lose the notification
            log.warning("mark_seen_failed", agent=AGENT_NAME, uid=uid, error=str(exc))

    async def _build_notification(self, message: EmailSummary) -> NotifyRequest:
        is_priority, matched = priority.evaluate(
            message.subject, message.snippet, self.settings.priority_keywords
        )

        verdict = await self.llm.chat_json(SUMMARY_SYSTEM_PROMPT, _summary_prompt(message))
        summary = ""
        if verdict:
            summary = " ".join(str(verdict.get("summary", "")).split())[:200]
            log.info(
                "priority_decision",
                agent=AGENT_NAME,
                uid=message.uid,
                keyword_priority=is_priority,
                matched=matched,
                # Logged for comparison only — the keyword match is what counts.
                llm_job_related=verdict.get("job_related"),
            )
        else:
            log.info(
                "priority_decision",
                agent=AGENT_NAME,
                uid=message.uid,
                keyword_priority=is_priority,
                matched=matched,
                llm_job_related=None,
            )

        return NotifyRequest(
            uid=message.uid,
            sender=message.sender,
            subject=message.subject,
            priority=is_priority,
            matched_keywords=matched,
            received_at=message.received_at,
            snippet=message.snippet[:400],
            summary=summary,
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        log.info("a2a_cancel_requested", agent=AGENT_NAME)
        raise NotImplementedError("scan_and_notify is a short synchronous skill")


def build_mailbox_app(settings: Settings) -> Starlette:
    endpoint = settings.agents.mailbox
    card = build_agent_card(
        name=AGENT_NAME,
        description=(
            "Reads the configured mailbox over MCP, flags top-priority mail and "
            "delegates notification to the WhatsApp notifier agent."
        ),
        url=endpoint.url,
        skills=[
            AgentSkill(
                id="scan_and_notify",
                name="Scan mailbox and notify",
                description=(
                    "List new mailbox messages, classify each as top priority using the "
                    "configured keywords, and send each one to the WhatsApp notifier agent."
                ),
                tags=["email", "imap", "triage"],
                examples=[json.dumps({"action": "scan_and_notify", "max_emails": 10})],
                input_modes=["application/json", "text/plain"],
                output_modes=["application/json"],
            )
        ],
    )
    return build_app(card, MailboxAgentExecutor(settings))
