from __future__ import annotations

from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentSkill
import httpx

from a2a_mail_notify.a2a_support import (
    build_agent_card,
    build_starlette_app,
    complete_text_task,
    parse_json_payload,
    request_text,
    send_a2a_text,
)
from a2a_mail_notify.config import Settings
from a2a_mail_notify.llm.ollama import OllamaClient
from a2a_mail_notify.logging import get_logger
from a2a_mail_notify.mcp_client import open_email_mcp
from a2a_mail_notify.models import EmailAlert
from a2a_mail_notify.services.mailbox import MailboxService
from a2a_mail_notify.storage.state_db import StateDB

log = get_logger(__name__)


MAILBOX_SKILL = AgentSkill(
    id="check_mailbox",
    name="Check mailbox",
    description="Fetch unread IMAP mail and notify the WhatsApp agent over A2A.",
    input_modes=["text/plain", "application/json"],
    output_modes=["application/json", "text/plain"],
    tags=["email", "imap", "a2a"],
    examples=["check mailbox", '{"max_emails": 5}'],
)


def mailbox_agent_card(settings: Settings):
    return build_agent_card(
        name="Mailbox Agent",
        description="Reads IMAP mail, flags job-related priority, and asks the WhatsApp agent to notify.",
        url=settings.agents.mailbox.url,
        skills=[MAILBOX_SKILL],
    )


class MailboxAgentExecutor(AgentExecutor):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ollama = OllamaClient(
            base_url=settings.ollama.base_url,
            model=settings.ollama.model,
            timeout_seconds=settings.ollama.timeout_seconds,
        )
        self.state_db = StateDB(settings.state_db_path)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        text = request_text(context)
        task_id = getattr(getattr(context, "current_task", None), "id", None)
        log.info(
            "a2a_inbound",
            agent="mailbox",
            skill="check_mailbox",
            task_id=str(task_id or ""),
            preview=text[:240],
        )
        payload = parse_json_payload(text)
        max_emails = payload.get("max_emails")
        await self.state_db.initialize()

        async def notify(alert: EmailAlert) -> None:
            await _notify_whatsapp_agent(self.settings, alert)

        async with open_email_mcp(
            self.settings.config_path,
            self.settings.logging.file,
            self.settings.logging.level,
        ) as email_mcp:
            service = MailboxService(
                settings=self.settings,
                ollama=self.ollama,
                state_db=self.state_db,
                email_mcp=email_mcp,
                notify=notify,
            )
            stats = await service.check_mailbox(max_emails=max_emails)

        result = stats.model_dump_json()
        log.info(
            "a2a_inbound_done",
            agent="mailbox",
            notified=stats.notified,
            errors=stats.errors,
            listed=stats.listed,
        )
        await complete_text_task(
            context,
            event_queue,
            result,
            working_message="Checking mailbox...",
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        log.warning("a2a_cancel_unsupported", agent="mailbox")
        raise NotImplementedError("Cancel is not supported.")


async def _notify_whatsapp_agent(settings: Settings, alert: EmailAlert) -> None:
    peer = settings.agents.whatsapp.url
    async with httpx.AsyncClient(timeout=settings.ollama.timeout_seconds) as http:
        resolver = A2ACardResolver(httpx_client=http, base_url=peer)
        card = await resolver.get_agent_card()
        log.info("a2a_discovered_peer", peer=peer, name=getattr(card, "name", "whatsapp"))
        client = await create_client(agent=card, client_config=ClientConfig(streaming=False))
        try:
            await send_a2a_text(client, alert.model_dump_json(), peer_url=peer, skill="notify_email")
        finally:
            await client.close()


def create_mailbox_app(settings: Settings):
    return build_starlette_app(mailbox_agent_card(settings), MailboxAgentExecutor(settings))
