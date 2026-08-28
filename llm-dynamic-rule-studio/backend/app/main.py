from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, fields, health, rules
from app.config import get_settings
from app.db import Base, engine
from app.seed import seed_field_definitions
from app.services.chat_jobs import ensure_chat_message_status_column


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await ensure_chat_message_status_column()
    await seed_field_definitions()
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="LLM Dynamic Rule Studio", version="1.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router, prefix="/api")
    app.include_router(rules.router, prefix="/api")
    app.include_router(fields.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    return app


app = create_app()
