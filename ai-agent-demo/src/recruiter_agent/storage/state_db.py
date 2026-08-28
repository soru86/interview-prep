from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from recruiter_agent.models import ProcessedEmailRecord, ProcessingStatus
from recruiter_agent.utils.logging import get_logger

log = get_logger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS processed_emails (
    message_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    match_score INTEGER,
    processed_at TEXT NOT NULL,
    error_message TEXT
);
"""


class StateDB:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    async def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(_SCHEMA)
            await db.commit()

    async def is_processed(self, message_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT 1 FROM processed_emails WHERE message_id = ?",
                (message_id,),
            )
            row = await cursor.fetchone()
            return row is not None

    async def mark_processed(self, record: ProcessedEmailRecord) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO processed_emails
                (message_id, status, match_score, processed_at, error_message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record.message_id,
                    record.status.value,
                    record.match_score,
                    record.processed_at.isoformat(),
                    record.error_message,
                ),
            )
            await db.commit()

    async def count_processed(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM processed_emails")
            row = await cursor.fetchone()
            return int(row[0]) if row else 0

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)
