from __future__ import annotations

import logging
import uuid

from sqlalchemy import select, text

from app.config import get_settings
from app.db import AsyncSessionLocal
from app.models.chat import ChatMessage
from app.models.field import FieldDefinition
from app.services.ollama_client import OllamaClient
from app.services.rule_generator import RuleGenerator

log = logging.getLogger(__name__)


def _count_conditions(node: dict) -> int:
    if node.get("type") == "condition":
        return 1
    total = 0
    for child in node.get("children", []):
        total += _count_conditions(child)
    return total


async def ensure_chat_message_status_column() -> None:
    """Add status column on existing DBs created before async chat landed."""
    async with AsyncSessionLocal() as session:
        await session.execute(
            text(
                """
                ALTER TABLE chat_messages
                ADD COLUMN IF NOT EXISTS status VARCHAR(50) NOT NULL DEFAULT 'complete'
                """
            )
        )
        await session.commit()


async def run_rule_generation_job(
    *,
    session_id: uuid.UUID,
    assistant_message_id: uuid.UUID,
    user_prompt: str,
) -> None:
    """Background worker: call Ollama and finalize the pending assistant message."""
    settings = get_settings()
    try:
        async with AsyncSessionLocal() as db:
            fields_result = await db.execute(
                select(FieldDefinition).order_by(FieldDefinition.key)
            )
            fields = list(fields_result.scalars().all())
            catalog = [
                {
                    "key": f.key,
                    "label": f.label,
                    "data_type": f.data_type,
                    "operators": f.operators,
                }
                for f in fields
            ]

        generator = RuleGenerator(OllamaClient(settings))
        raw, generated = await generator.generate(user_prompt, catalog)
        summary = (
            f"Generated rule **{generated.name}** with "
            f"{_count_conditions(generated.condition_tree.model_dump())} condition(s). "
            "Use Add to Rule Screen to apply it."
        )

        async with AsyncSessionLocal() as db:
            assistant = await db.get(ChatMessage, assistant_message_id)
            if not assistant:
                log.error("Assistant message %s missing", assistant_message_id)
                return
            assistant.content = summary
            assistant.generated_payload = generated.model_dump()
            assistant.status = "complete"
            await db.commit()
            log.info(
                "Chat generation complete session=%s assistant=%s",
                session_id,
                assistant_message_id,
            )
    except Exception as exc:
        log.exception("Chat generation failed session=%s", session_id)
        async with AsyncSessionLocal() as db:
            assistant = await db.get(ChatMessage, assistant_message_id)
            if not assistant:
                return
            assistant.content = f"Could not generate a rule from that prompt: {exc}"
            assistant.generated_payload = None
            assistant.status = "error"
            await db.commit()
