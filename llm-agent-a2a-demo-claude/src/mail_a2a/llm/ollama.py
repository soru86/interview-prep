"""Ollama chat client for DeepSeek R1 1.5B.

R1 is a reasoning model: it emits a <think>...</think> block before the answer.
Callers want the answer, so the block is stripped (and logged at debug level, it
is genuinely useful when a prompt misbehaves).
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

import httpx

from mail_a2a.config import OllamaSettings
from mail_a2a.logging_setup import get_logger

log = get_logger(__name__)

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_ORPHAN_OPEN = re.compile(r"<think>.*", re.DOTALL | re.IGNORECASE)


def strip_reasoning(text: str) -> str:
    """Remove DeepSeek R1's chain-of-thought block from a completion."""
    cleaned = _THINK_BLOCK.sub("", text or "")
    # A truncated response can leave an unclosed <think>; drop the tail.
    cleaned = _ORPHAN_OPEN.sub("", cleaned)
    return cleaned.strip()


def _extract_json_object(text: str) -> dict[str, Any] | None:
    """Best-effort JSON object recovery from a chatty completion."""
    text = text.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        parsed = json.loads(text[start : end + 1])
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


class OllamaUnavailable(RuntimeError):
    """Raised when the model cannot be reached and the config marks it required."""


class OllamaClient:
    """Thin async wrapper over Ollama's /api/chat."""

    def __init__(self, settings: OllamaSettings, *, agent: str = "") -> None:
        self.settings = settings
        self.agent = agent
        self._base_url = settings.base_url.rstrip("/")

    async def health(self) -> dict[str, Any]:
        """Check the daemon is up and the configured model is pulled."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self._base_url}/api/tags")
                response.raise_for_status()
                models = [item.get("name", "") for item in response.json().get("models", [])]
        except Exception as exc:
            log.warning("ollama_health_failed", base_url=self._base_url, error=str(exc))
            return {"ok": False, "error": str(exc), "models": []}

        # Ollama reports "deepseek-r1:1.5b"; accept a bare name without the tag too.
        wanted = self.settings.model
        present = wanted in models or any(m.split(":")[0] == wanted.split(":")[0] for m in models)
        log.info(
            "ollama_health",
            base_url=self._base_url,
            model=wanted,
            model_present=present,
            available=models,
        )
        return {"ok": True, "model_present": present, "models": models}

    async def chat(self, system: str, user: str, *, max_tokens: int = 400) -> str:
        """Send a single-turn chat and return the answer with reasoning stripped."""
        payload = {
            "model": self.settings.model,
            "stream": False,
            # R1 reasons before answering. Left on, it spends the whole token
            # budget inside <think> and the answer comes back empty; Ollama's
            # `think` flag keeps the reasoning out of `message.content`.
            "think": self.settings.think,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "temperature": self.settings.temperature,
                "num_predict": max_tokens,
            },
        }
        started = time.perf_counter()
        log.info(
            "llm_request",
            agent=self.agent,
            model=self.settings.model,
            prompt_chars=len(user),
        )
        try:
            async with httpx.AsyncClient(timeout=self.settings.timeout_seconds) as client:
                response = await client.post(f"{self._base_url}/api/chat", json=payload)
                response.raise_for_status()
                body = response.json()
        except Exception as exc:
            duration_ms = round((time.perf_counter() - started) * 1000, 1)
            log.warning(
                "llm_request_failed",
                agent=self.agent,
                model=self.settings.model,
                duration_ms=duration_ms,
                error=str(exc),
            )
            if self.settings.required:
                raise OllamaUnavailable(str(exc)) from exc
            return ""

        message = body.get("message") or {}
        # Ollama returns the reasoning separately when the model supports it;
        # strip_reasoning covers versions that inline it as <think>.
        answer = strip_reasoning(message.get("content", "") or "")
        thinking = message.get("thinking") or ""
        duration_ms = round((time.perf_counter() - started) * 1000, 1)
        truncated = body.get("done_reason") == "length"
        log.info(
            "llm_response",
            agent=self.agent,
            model=self.settings.model,
            duration_ms=duration_ms,
            answer_chars=len(answer),
            eval_count=body.get("eval_count"),
            truncated=truncated or None,
        )
        if thinking.strip():
            log.debug("llm_reasoning", agent=self.agent, preview=thinking.strip()[:400])
        return answer

    async def chat_json(
        self, system: str, user: str, *, max_tokens: int = 400
    ) -> dict[str, Any] | None:
        """Same as `chat`, but parse the answer as a JSON object."""
        answer = await self.chat(system, user, max_tokens=max_tokens)
        parsed = _extract_json_object(answer)
        if parsed is None and answer:
            log.warning("llm_json_parse_failed", agent=self.agent, preview=answer[:200])
        return parsed
