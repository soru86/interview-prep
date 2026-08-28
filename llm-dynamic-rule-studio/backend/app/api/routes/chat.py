import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import (
    ChatMessageAccepted,
    ChatMessageCreate,
    ChatMessageOut,
    ChatSessionCreate,
    ChatSessionOut,
)
from app.services.chat_jobs import run_rule_generation_job

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: ChatSessionCreate, db: AsyncSession = Depends(get_db)
) -> ChatSession:
    session = ChatSession(rule_id=payload.rule_id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
async def get_session(
    session_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ChatSession:
    session = await db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
async def list_messages(
    session_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[ChatMessage]:
    session = await db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return list(result.scalars().all())


@router.get("/messages/{message_id}", response_model=ChatMessageOut)
async def get_message(
    message_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ChatMessage:
    message = await db.get(ChatMessage, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatMessageAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def post_message(
    session_id: uuid.UUID,
    payload: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
) -> ChatMessageAccepted:
    session = await db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=payload.content,
        status="complete",
        generated_payload=None,
    )
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content="Generating with DeepSeek R1… this can take a few minutes. Keep this tab open.",
        status="pending",
        generated_payload=None,
    )
    db.add(user_msg)
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(user_msg)
    await db.refresh(assistant_msg)

    asyncio.create_task(
        run_rule_generation_job(
            session_id=session.id,
            assistant_message_id=assistant_msg.id,
            user_prompt=payload.content,
        )
    )

    return ChatMessageAccepted(
        user_message=ChatMessageOut.model_validate(user_msg),
        assistant_message=ChatMessageOut.model_validate(assistant_msg),
        poll_url=f"/api/chat/messages/{assistant_msg.id}",
    )
