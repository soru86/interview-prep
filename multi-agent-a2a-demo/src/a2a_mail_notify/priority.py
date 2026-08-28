from __future__ import annotations

import re


def is_top_priority(text: str, keywords: list[str]) -> bool:
    """True when any keyword appears as a whole word (case-insensitive)."""
    haystack = text or ""
    for keyword in keywords:
        token = keyword.strip()
        if not token:
            continue
        if re.search(rf"\b{re.escape(token)}\b", haystack, flags=re.IGNORECASE):
            return True
    return False
