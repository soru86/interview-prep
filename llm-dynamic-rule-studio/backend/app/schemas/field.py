import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FieldCreate(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=255)
    data_type: str = Field(min_length=1, max_length=50)
    operators: list[str] = Field(default_factory=list)


class FieldOut(BaseModel):
    id: uuid.UUID
    key: str
    label: str
    data_type: str
    operators: list
    created_at: datetime

    model_config = {"from_attributes": True}
