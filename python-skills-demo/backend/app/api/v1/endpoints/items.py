"""Items endpoints — placeholder resource to demonstrate a second router."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/items", tags=["items"])


# ---------------------------------------------------------------------------
# Schemas (inline for simplicity — move to app/schemas/item.py as it grows)
# ---------------------------------------------------------------------------

class ItemCreate(BaseModel):
    title: str
    description: str | None = None


class ItemResponse(BaseModel):
    id: int
    title: str
    description: str | None
    owner_id: int


# ---------------------------------------------------------------------------
# In-memory store (replace with real DB model/CRUD later)
# ---------------------------------------------------------------------------
_items: list[dict] = []
_next_id: int = 1


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(
    payload: ItemCreate,
    current_user: User = Depends(get_current_user),
):
    """Create an item owned by the current user."""
    global _next_id
    item = {
        "id": _next_id,
        "title": payload.title,
        "description": payload.description,
        "owner_id": current_user.id,
    }
    _items.append(item)
    _next_id += 1
    return item


@router.get("/", response_model=list[ItemResponse])
def list_items(_current_user: User = Depends(get_current_user)):
    """List all items."""
    return _items


@router.get("/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, _current_user: User = Depends(get_current_user)):
    """Get a single item by ID."""
    for item in _items:
        if item["id"] == item_id:
            return item
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Item not found")
