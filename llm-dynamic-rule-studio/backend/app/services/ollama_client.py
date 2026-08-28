from __future__ import annotations

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import Settings


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.timeout_seconds = settings.ollama_timeout_seconds

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.RemoteProtocolError)),
        reraise=True,
    )
    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json",
            "think": False,
            "options": {
                "temperature": temperature,
                # Enough for a rule JSON; keep low so CPU finishes quickly.
                "num_predict": 1024,
            },
        }
        timeout = httpx.Timeout(
            connect=30.0,
            read=float(self.timeout_seconds),
            write=60.0,
            pool=30.0,
        )
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            message = data.get("message") or {}
            content = (message.get("content") or "").strip()
            thinking = (message.get("thinking") or message.get("reasoning") or "").strip()
            if content:
                return content
            if thinking:
                return thinking
            raise ValueError(
                "Empty response from Ollama "
                f"(done_reason={data.get('done_reason')!r}, "
                f"eval_count={data.get('eval_count')!r})."
            )

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
