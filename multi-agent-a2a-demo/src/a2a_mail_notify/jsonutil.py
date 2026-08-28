from __future__ import annotations

import json
import re


def strip_think_blocks(text: str) -> str:
    think_open = "<" + "think" + ">"
    think_close = "<" + "/think" + ">"
    reason_open = "<" + "redacted_reasoning" + ">"
    reason_close = "<" + "/redacted_reasoning" + ">"
    for pattern in (
        think_open + r".*?" + think_close,
        reason_open + r".*?" + reason_close,
    ):
        text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()


def extract_json_object(text: str) -> dict:
    """Extract the first JSON object from LLM output (handles markdown/thinking blocks)."""
    text = strip_think_blocks(text)
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM response.")
    return json.loads(text[start : end + 1])
