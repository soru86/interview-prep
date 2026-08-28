"""Shared A2A plumbing: agent cards, JSON-RPC apps, and a JSON request helper.

Both agents are real A2A servers — they publish an Agent Card at
`/.well-known/agent-card.json` and accept `message/send` over JSON-RPC — so the
mailbox agent talks to the notifier agent purely as an A2A client.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Any

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_message_text, new_task_from_user_message, new_text_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
    Role,
    SendMessageRequest,
    TaskState,
)
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from starlette.applications import Starlette

from mail_a2a.logging_setup import get_logger

log = get_logger(__name__)

PROTOCOL_BINDING = "JSONRPC"


def build_agent_card(
    *,
    name: str,
    description: str,
    url: str,
    skills: list[AgentSkill],
    version: str = "1.0.0",
) -> AgentCard:
    """An A2A Agent Card describing what this agent can do and how to reach it."""
    return AgentCard(
        name=name,
        description=description,
        version=version,
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["application/json", "text/plain"],
        # Non-streaming: each skill is a short request/response round trip.
        capabilities=AgentCapabilities(streaming=False),
        skills=skills,
        supported_interfaces=[
            AgentInterface(protocol_binding=PROTOCOL_BINDING, url=url, protocol_version="1.0")
        ],
    )


def build_app(card: AgentCard, executor: AgentExecutor) -> Starlette:
    """Starlette app serving the agent card plus the A2A JSON-RPC endpoint."""
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )
    routes = [*create_agent_card_routes(card), *create_jsonrpc_routes(handler, "/")]
    log.info(
        "a2a_server_ready",
        agent=card.name,
        url=card.supported_interfaces[0].url,
        card_path=AGENT_CARD_WELL_KNOWN_PATH,
        skills=[skill.id for skill in card.skills],
    )
    return Starlette(routes=routes)


# --- server side helpers ----------------------------------------------------


def request_text(context: RequestContext) -> str:
    try:
        return (get_message_text(context.message) or "").strip()
    except Exception:  # pragma: no cover - defensive
        return ""


def parse_json(text: str) -> dict[str, Any]:
    """Parse a JSON object out of an A2A text part, tolerating surrounding prose."""
    text = (text or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            return {}
        try:
            parsed = json.loads(text[start : end + 1])
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}


async def complete_with_json(
    context: RequestContext,
    event_queue: EventQueue,
    payload: dict[str, Any],
    *,
    working_message: str = "Working",
) -> None:
    """Drive a task through working -> artifact -> completed with a JSON result."""
    task = context.current_task or new_task_from_user_message(context.message)
    if context.current_task is None:
        await event_queue.enqueue_event(task)

    updater = TaskUpdater(event_queue=event_queue, task_id=task.id, context_id=task.context_id)
    await updater.update_status(
        state=TaskState.TASK_STATE_WORKING,
        message=new_text_message(working_message),
    )
    await updater.add_artifact(
        parts=[new_text_part(text=json.dumps(payload), media_type="application/json")]
    )
    await updater.update_status(
        state=TaskState.TASK_STATE_COMPLETED,
        message=new_text_message("Completed"),
    )


# --- client side helpers ----------------------------------------------------


def _part_texts(parts: Any, sink: list[str]) -> None:
    for part in parts or []:
        if text := getattr(part, "text", ""):
            sink.append(text)


def _has(message: Any, field: str) -> bool:
    try:
        return message.HasField(field)
    except (ValueError, AttributeError):  # pragma: no cover - defensive
        return False


def result_texts(event: Any) -> list[str]:
    """Text of the *result* parts of one A2A stream response.

    Only artifacts and status messages are read. A completed Task also carries
    `history`, which echoes the request we just sent — including that would make
    a caller parse its own payload back as the peer's answer.
    """
    sink: list[str] = []
    if _has(event, "task"):
        task = event.task
        for artifact in task.artifacts:
            _part_texts(artifact.parts, sink)
        if not sink and _has(task.status, "message"):
            _part_texts(task.status.message.parts, sink)
    elif _has(event, "message"):
        _part_texts(event.message.parts, sink)
    elif _has(event, "artifact_update"):
        _part_texts(event.artifact_update.artifact.parts, sink)
    elif _has(event, "status_update") and _has(event.status_update.status, "message"):
        _part_texts(event.status_update.status.message.parts, sink)
    return sink


def _last_json(candidates: list[str]) -> dict[str, Any]:
    """The agent's result artifact is the last well-formed JSON object in the stream."""
    for text in reversed(candidates):
        if parsed := parse_json(text):
            return parsed
    return {}


@asynccontextmanager
async def open_a2a_client(peer_url: str, *, timeout_seconds: float = 300.0):
    """Resolve a peer's Agent Card and yield a JSON-RPC client for it.

    The timeout is deliberately generous: a skill call blocks until the peer has
    finished its own LLM inference, and the first DeepSeek request pays for the
    model load as well.
    """
    async with httpx.AsyncClient(timeout=timeout_seconds) as http:
        client = await create_client(peer_url, ClientConfig(streaming=False, httpx_client=http))
        card = client._card  # noqa: SLF001 - the SDK keeps the resolved card private
        log.info(
            "a2a_peer_resolved",
            peer=peer_url,
            agent=card.name,
            skills=[skill.id for skill in card.skills],
        )
        yield client


async def send_json(client: Any, payload: dict[str, Any], *, peer: str, skill: str) -> dict[str, Any]:
    """Send a JSON payload as an A2A message and return the peer's JSON result."""
    text = json.dumps(payload)
    log.info("a2a_send", peer=peer, skill=skill, payload_chars=len(text))

    request = SendMessageRequest(message=new_text_message(text, role=Role.ROLE_USER))
    collected: list[str] = []
    async for event in client.send_message(request):
        collected.extend(result_texts(event))

    result = _last_json(collected)
    if not result:
        log.error("a2a_no_result", peer=peer, skill=skill, chunks=len(collected))
    log.info("a2a_reply", peer=peer, skill=skill, keys=sorted(result.keys()))
    return result
