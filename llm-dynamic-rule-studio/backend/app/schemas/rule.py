import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.condition import ConditionTree


class RuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: str = "draft"
    condition_tree: ConditionTree | dict[str, Any]


class RuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = None
    condition_tree: ConditionTree | dict[str, Any] | None = None


class RuleOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    status: str
    condition_tree: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
