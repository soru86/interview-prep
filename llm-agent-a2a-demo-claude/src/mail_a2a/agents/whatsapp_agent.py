"""Agent 2 — the WhatsApp notifier.

Receives a notification request over A2A from the mailbox agent, phrases it with
DeepSeek R1, and delivers it through the `whatsapp-mcp` tool server.

The sender, subject and TOP PRIORITY flag are laid out by a fixed template, not
by the model — those three lines are the contract with the user and must not
depend on what a 1.5B model decides to write. The model only contributes one
line of context underneath.
"""

from __future__ import annotations

import json
import re

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentSkill
from starlette.applications import Starlette

from mail_a2a.a2a_common import build_agent_card, build_app, complete_with_json, parse_json, request_text
from mail_a2a.config import Settings
from mail_a2a.llm import OllamaClient
from mail_a2a.logging_setup import get_logger
from mail_a2a.mcp_client import open_whatsapp_mcp
from mail_a2a.models import NotifyRequest, NotifyResult

log = get_logger(__name__)

AGENT_NAME = "whatsapp-notifier-agent"

SYSTEM_PROMPT = (
    "Summarize an email in ONE short sentence for a phone notification. "
    "Answer with that sentence only: no preamble, no quotes, no emoji, no markdown. "
    'Example answer: "A recruiter is asking about your availability for a call."'
)


MAX_CONTEXT_WORDS = 24


def one_line(text: str) -> str:
    """Squeeze a model answer into a single short sentence.

    A 1.5B model does not reliably respect "one line, 20 words", so the length
    limit is enforced here rather than trusted to the prompt.
    """
    cleaned = " ".join((text or "").split())
    cleaned = cleaned.strip("`\"'* ")
    if not cleaned:
        return ""
    first_sentence = re.split(r"(?<=[.!?])\s", cleaned, maxsplit=1)[0]
    words = first_sentence.split()
    if len(words) > MAX_CONTEXT_WORDS:
        return " ".join(words[:MAX_CONTEXT_WORDS]) + "…"
    return first_sentence


def _context_prompt(request: NotifyRequest) -> str:
    return (
        f"Sender: {request.sender}\n"
        f"Subject: {request.subject}\n"
        f"Summary so far: {request.summary or '(none)'}\n"
        f"Body snippet: {request.snippet[:400] or '(none)'}\n\n"
        "Write the one-line context note."
    )


def render_message(request: NotifyRequest, context_line: str = "") -> str:
    """The exact WhatsApp text. Sender, subject and priority flag are guaranteed."""
    lines: list[str] = []
    if request.priority:
        matched = ", ".join(request.matched_keywords)
        lines.append("🚩 *TOP PRIORITY*" + (f" ({matched})" if matched else ""))
    lines.append("📧 *New email*")
    lines.append(f"*From:* {request.sender}")
    lines.append(f"*Subject:* {request.subject}")
    if request.received_at:
        lines.append(f"*Received:* {request.received_at}")
    if context_line:
        lines.append("")
        lines.append(context_line)
    return "\n".join(lines)


class WhatsAppAgentExecutor(AgentExecutor):
    """A2A skill: `notify_whatsapp`."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.llm = OllamaClient(settings.ollama, agent=AGENT_NAME)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        raw = request_text(context)
        log.info("a2a_received", agent=AGENT_NAME, skill="notify_whatsapp", payload_chars=len(raw))

        try:
            request = NotifyRequest.model_validate(parse_json(raw))
        except Exception as exc:
            log.error("a2a_bad_request", agent=AGENT_NAME, error=str(exc), preview=raw[:200])
            await complete_with_json(
                context,
                event_queue,
                NotifyResult(ok=False, error=f"invalid notify request: {exc}").model_dump(),
            )
            return

        log.info(
            "notification_requested",
            agent=AGENT_NAME,
            uid=request.uid,
            sender=request.sender,
            subject=request.subject,
            priority=request.priority,
        )

        # A chatty or unavailable model must never break delivery, so the answer
        # is trimmed here and the template below does not depend on it.
        context_line = one_line(
            await self.llm.chat(SYSTEM_PROMPT, _context_prompt(request), max_tokens=500)
        )
        text = render_message(request, context_line)

        result = await self._deliver(request, text)
        log.info(
            "notification_finished",
            agent=AGENT_NAME,
            uid=request.uid,
            ok=result.ok,
            provider=result.provider,
        )
        await complete_with_json(context, event_queue, result.model_dump())

    async def _deliver(self, request: NotifyRequest, text: str) -> NotifyResult:
        try:
            async with open_whatsapp_mcp() as mcp:
                payload = await mcp.call(
                    "send_whatsapp_message",
                    {
                        "text": text,
                        "to": self.settings.whatsapp.to,
                        "priority": request.priority,
                    },
                )
        except Exception as exc:
            log.error("notification_failed", agent=AGENT_NAME, uid=request.uid, error=str(exc))
            return NotifyResult(uid=request.uid, ok=False, text=text, error=str(exc))

        if isinstance(payload, str):
            payload = parse_json(payload) or {"ok": False, "error": payload}

        return NotifyResult(
            uid=request.uid,
            ok=bool(payload.get("ok")),
            provider=str(payload.get("provider", self.settings.whatsapp.provider)),
            to=str(payload.get("to", self.settings.whatsapp.to)),
            message_id=str(payload.get("message_id", "")),
            text=text,
            error=str(payload.get("error", "")),
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        log.info("a2a_cancel_requested", agent=AGENT_NAME)
        raise NotImplementedError("notify_whatsapp is a short synchronous skill")


def build_whatsapp_app(settings: Settings) -> Starlette:
    endpoint = settings.agents.whatsapp
    card = build_agent_card(
        name=AGENT_NAME,
        description=(
            "Delivers WhatsApp notifications about incoming email, flagging "
            "top-priority messages."
        ),
        url=endpoint.url,
        skills=[
            AgentSkill(
                id="notify_whatsapp",
                name="Notify on WhatsApp",
                description=(
                    "Given an email's sender, subject and priority flag, compose and send "
                    "a WhatsApp notification to the configured number."
                ),
                tags=["whatsapp", "notification", "messaging"],
                examples=[
                    json.dumps(
                        {
                            "uid": "42",
                            "sender": "Recruiter <talent@example.com>",
                            "subject": "Senior Engineer position",
                            "priority": True,
                            "matched_keywords": ["position"],
                        }
                    )
                ],
                input_modes=["application/json", "text/plain"],
                output_modes=["application/json"],
            )
        ],
    )
    return build_app(card, WhatsAppAgentExecutor(settings))
