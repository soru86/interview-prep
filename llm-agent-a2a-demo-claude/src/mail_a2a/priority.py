"""Top-priority detection.

Deliberately deterministic: a 1.5B model is fine for phrasing a notification but
not something to trust with "did this email contain the word 'position'". The
LLM opinion is logged alongside for comparison, it never overrides this.
"""

from __future__ import annotations

import re
from functools import lru_cache

DEFAULT_KEYWORDS = ("job", "opportunity", "opening", "position")


@lru_cache(maxsize=32)
def _pattern(keywords: tuple[str, ...]) -> re.Pattern[str]:
    # \b keeps "position" from firing on "repositioning"; plural/possessive
    # suffixes still match so "openings" and "job's" are caught.
    alternatives = "|".join(re.escape(word.strip()) for word in keywords if word.strip())
    return re.compile(rf"\b({alternatives})(?:s|es|'s)?\b", re.IGNORECASE)


def match_keywords(text: str, keywords: list[str] | tuple[str, ...] | None = None) -> list[str]:
    """Return the configured keywords present in `text`, in config order."""
    words = tuple(keywords) if keywords else DEFAULT_KEYWORDS
    if not text or not any(w.strip() for w in words):
        return []
    hits = {hit.group(1).lower() for hit in _pattern(words).finditer(text)}
    return [word for word in words if word.lower() in hits]


def evaluate(
    subject: str,
    body: str = "",
    keywords: list[str] | tuple[str, ...] | None = None,
) -> tuple[bool, list[str]]:
    """(is_top_priority, matched_keywords) for an email's subject + body."""
    matched = match_keywords(f"{subject}\n{body}", keywords)
    return bool(matched), matched
