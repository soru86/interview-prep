"""Remembers which messages were already notified, so a poll loop stays quiet."""

from __future__ import annotations

import json
from pathlib import Path

from mail_a2a.logging_setup import get_logger

log = get_logger(__name__)

MAX_REMEMBERED = 500


class SeenStore:
    """A small JSON-backed set of mailbox UIDs that have been notified."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._uids: list[str] = []
        self._load()

    def _load(self) -> None:
        if not self.path.is_file():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self._uids = [str(uid) for uid in data.get("seen", [])]
            log.info("state_loaded", path=str(self.path), count=len(self._uids))
        except (OSError, json.JSONDecodeError) as exc:
            log.warning("state_unreadable", path=str(self.path), error=str(exc))
            self._uids = []

    def has(self, uid: str) -> bool:
        return uid in self._uids

    def add(self, uid: str) -> None:
        if uid in self._uids:
            return
        self._uids.append(uid)
        # Keep the newest entries only; old UIDs will never be seen again anyway.
        if len(self._uids) > MAX_REMEMBERED:
            self._uids = self._uids[-MAX_REMEMBERED:]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"seen": self._uids}, indent=2), encoding="utf-8")
        log.info("state_saved", path=str(self.path), count=len(self._uids))
