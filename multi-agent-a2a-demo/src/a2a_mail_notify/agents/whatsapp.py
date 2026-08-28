from __future__ import annotations

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentSkill

from a2a_mail_notify.a2a_support import (
    build_agent_card,
    build_starlette_app,
    complete_text_task,
    parse_json_payload,
    request_text,
)
from a2a_mail_notify.config import Settings
from a2a_mail_notify.llm.ollama import OllamaClient
from a2a_mail_notify.logging import get_logger
from a2a_mail_notify.mcp_client import open_whatsapp_mcp
from a2a_mail_notify.models import EmailAlert
from a2a_mail_notify.services.whatsapp import WhatsAppService

log = get_logger(__name__)


WHATSAPP_SKILL = AgentSkill(
    id="notify_email",
    name="Notify email",
    description="Send a WhatsApp alert with email sender, subject, and optional TOP PRIORITY flag.",
    input_modes=["application/json", "text/plain"],
    output_modes=["application/json", "text/plain"],
    tags=["whatsapp", "notify", "a2a"],
    examples=['{"sender": "Ada <ada@example.com>", "subject": "Job opening", "priority": true}'],
)


def whatsapp_agent_card(settings: Settings):
    return build_agent_card(
        name="WhatsApp Agent",
        description="Formats email alerts and sends them to the configured WhatsApp number.",
        url=settings.agents.whatsapp.url,
        skills=[WHATSAPP_SKILL],
    )


class WhatsAppAgentExecutor(AgentExecutor):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ollama = OllamaClient(
            base_url=settings.ollama.base_url,
            model=settings.ollama.model,
            timeout_seconds=settings.ollama.timeout_seconds,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        text = request_text(context)
        task_id = getattr(getattr(context, "current_task", None), "id", None)
        log.info(
            "a2a_inbound",
            agent="whatsapp",
            skill="notify_email",
            task_id=str(task_id or ""),
            preview=text[:240],
        )
        payload = parse_json_payload(text)
        if not payload:
            raise ValueError("WhatsApp agent expects JSON with sender, subject, priority.")
        alert = EmailAlert.model_validate(payload)

        async with open_whatsapp_mcp(
            self.settings.config_path,
            self.settings.logging.file,
            self.settings.logging.level,
        ) as whatsapp_mcp:
            service = WhatsAppService(self.settings, self.ollama, whatsapp_mcp)
            result = await service.notify(alert)

        log.info(
            "a2a_inbound_done",
            agent="whatsapp",
            ok=result.ok,
            dry_run=result.dry_run,
            provider=result.provider,
        )
        await complete_text_task(
            context,
            event_queue,
            result.model_dump_json(),
            working_message="Sending WhatsApp notification...",
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        log.warning("a2a_cancel_unsupported", agent="whatsapp")
        raise NotImplementedError("Cancel is not supported.")


def create_whatsapp_app(settings: Settings):
    return build_starlette_app(whatsapp_agent_card(settings), WhatsAppAgentExecutor(settings))
