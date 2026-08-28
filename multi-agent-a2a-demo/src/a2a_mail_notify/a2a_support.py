from __future__ import annotations

import json
from typing import Any

from a2a.helpers import (
    get_message_text,
    new_task_from_user_message,
    new_text_message,
    new_text_part,
)
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    Role,
    SendMessageRequest,
    TaskState,
)
from starlette.applications import Starlette

from a2a_mail_notify.logging import get_logger

log = get_logger(__name__)

try:
    from a2a.types import AgentInterface
except ImportError:  # older a2a-sdk
    AgentInterface = None  # type: ignore[misc, assignment]


def build_agent_card(
    *,
    name: str,
    description: str,
    url: str,
    skills: list[AgentSkill],
) -> AgentCard:
    capabilities = AgentCapabilities(streaming=False)
    common = {
        "name": name,
        "description": description,
        "version": "1.0.0",
        "default_input_modes": ["text/plain"],
        "default_output_modes": ["application/json", "text/plain"],
        "capabilities": capabilities,
        "skills": skills,
    }
    if AgentInterface is not None:
        try:
            return AgentCard(
                **common,
                supported_interfaces=[
                    AgentInterface(
                        protocol_binding="JSONRPC",
                        url=url,
                        protocol_version="1.0",
                    )
                ],
            )
        except Exception:
            pass
    return AgentCard(**common, url=url)


def build_starlette_app(agent_card: AgentCard, executor: AgentExecutor) -> Starlette:
    handler_kwargs: dict[str, Any] = {
        "agent_executor": executor,
        "task_store": InMemoryTaskStore(),
    }
    try:
        request_handler = DefaultRequestHandler(**handler_kwargs, agent_card=agent_card)
    except TypeError:
        request_handler = DefaultRequestHandler(**handler_kwargs)

    routes = []
    routes.extend(create_agent_card_routes(agent_card))
    routes.extend(create_jsonrpc_routes(request_handler, "/"))
    log.info("a2a_server_routes_ready", agent=agent_card.name, url=_card_url(agent_card))
    return Starlette(routes=routes)


def _card_url(card: AgentCard) -> str:
    interfaces = getattr(card, "supported_interfaces", None) or []
    if interfaces:
        return getattr(interfaces[0], "url", "") or ""
    return getattr(card, "url", "") or ""


async def complete_text_task(
    context: RequestContext,
    event_queue: EventQueue,
    result_text: str,
    working_message: str = "Working...",
) -> None:
    if context.current_task:
        task = context.current_task
    else:
        task = new_task_from_user_message(context.message)
        await event_queue.enqueue_event(task)

    updater = TaskUpdater(event_queue=event_queue, task_id=task.id, context_id=task.context_id)
    await updater.update_status(
        state=TaskState.TASK_STATE_WORKING,
        message=new_text_message(working_message),
    )
    await updater.add_artifact(parts=[new_text_part(text=result_text, media_type="text/plain")])
    await updater.update_status(
        state=TaskState.TASK_STATE_COMPLETED,
        message=new_text_message("Completed"),
    )


def request_text(context: RequestContext) -> str:
    try:
        return (get_message_text(context.message) or "").strip()
    except Exception:
        return ""


def parse_json_payload(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                data = json.loads(text[start : end + 1])
                return data if isinstance(data, dict) else {}
            except json.JSONDecodeError:
                return {}
        return {}


def _collect_text(value: Any, acc: list[str]) -> None:
    if value is None or isinstance(value, (bool, int, float, bytes)):
        return
    if isinstance(value, str):
        if value.strip():
            acc.append(value)
        return
    if isinstance(value, dict):
        for item in value.values():
            _collect_text(item, acc)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _collect_text(item, acc)
        return
    if hasattr(value, "ListFields"):
        try:
            for _field, field_value in value.ListFields():
                _collect_text(field_value, acc)
            return
        except Exception:
            pass
    for attr in (
        "text",
        "message",
        "result",
        "artifact",
        "artifacts",
        "parts",
        "root",
        "task",
        "status_update",
        "artifact_update",
    ):
        if hasattr(value, attr):
            _collect_text(getattr(value, attr), acc)


async def send_a2a_text(client: Any, text: str, peer_url: str, skill: str) -> str:
    log.info("a2a_outbound", peer=peer_url, skill=skill, preview=text[:240])
    message = new_text_message(text, role=Role.ROLE_USER)
    request = SendMessageRequest(message=message)
    collected: list[str] = []
    async for chunk in client.send_message(request):
        log.debug("a2a_chunk", peer=peer_url, chunk_type=type(chunk).__name__)
        _collect_text(chunk, collected)
    unique = list(dict.fromkeys(item.strip() for item in collected if item and item.strip()))
    result = _prefer_json_text(unique)
    log.info("a2a_outbound_done", peer=peer_url, skill=skill, preview=result[:240])
    return result


def _prefer_json_text(candidates: list[str]) -> str:
    json_hits = []
    for item in candidates:
        try:
            json.loads(item)
        except json.JSONDecodeError:
            continue
        json_hits.append(item)
    if json_hits:
        return json_hits[-1]
    return candidates[-1] if candidates else ""
