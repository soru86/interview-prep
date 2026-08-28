import json
import re
from typing import Any


THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def strip_think_blocks(text: str) -> str:
    return THINK_RE.sub("", text).strip()


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = strip_think_blocks(text)
    cleaned = cleaned.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model response.")

    data = json.loads(cleaned[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("Extracted JSON is not an object.")
    return data
