import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.condition import GeneratedRulePayload


class ChatSessionCreate(BaseModel):
    rule_id: uuid.UUID | None = None


class ChatSessionOut(BaseModel):
    id: uuid.UUID
    rule_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1)


class ChatMessageOut(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    status: str = "complete"
    generated_payload: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageAccepted(BaseModel):
    """Returned immediately; poll messages until assistant status is complete/error."""

    user_message: ChatMessageOut
    assistant_message: ChatMessageOut
    poll_url: str


# Keep for backwards compatibility if needed
class ChatMessageResponse(BaseModel):
    user_message: ChatMessageOut
    assistant_message: ChatMessageOut
    generated_payload: GeneratedRulePayload | None = None
