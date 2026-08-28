from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.services.ollama_client import OllamaClient

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    settings = get_settings()
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    ollama = OllamaClient(settings)
    ollama_ok = await ollama.health()

    status = "ok" if db_ok and ollama_ok else "degraded"
    return {
        "status": status,
        "database": db_ok,
        "ollama": ollama_ok,
        "model": settings.ollama_model,
    }
