"""Pydantic DTOs for User request / response validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Payload for creating a new user."""

    email: EmailStr
    password: str
    full_name: str | None = None


class UserUpdate(BaseModel):
    """Payload for partially updating a user."""

    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """Public-facing user representation (password never exposed)."""

    id: int
    email: str
    full_name: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class Token(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Extracted token claims."""

    email: str | None = None
