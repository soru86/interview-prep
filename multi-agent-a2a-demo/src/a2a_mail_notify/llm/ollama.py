from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from a2a_mail_notify.jsonutil import extract_json_object, strip_think_blocks
from a2a_mail_notify.logging import get_logger

log = get_logger(__name__)


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout_seconds: int = 180) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=20))
    async def _chat(self, system: str, user: str, temperature: float = 0.2) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": temperature},
        }
        log.debug("ollama_request", model=self.model, prompt=user[:500])
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "")
            if not content:
                raise ValueError("Empty response from Ollama.")
            log.debug("ollama_response", model=self.model, content=content[:800])
            return content

    async def extract_email_fields(self, sender: str, subject: str, body: str) -> dict[str, str]:
        system = (
            "You extract sender and subject from an email. "
            "Respond with ONLY valid JSON, no markdown."
        )
        user = f"""Sender header: {sender}
Subject header: {subject}
Body excerpt:
{body[:3000]}

Return JSON with keys: sender, subject"""
        try:
            raw = await self._chat(system, user, temperature=0.0)
            data = extract_json_object(raw)
            return {
                "sender": str(data.get("sender") or sender).strip() or sender,
                "subject": str(data.get("subject") or subject).strip() or subject,
            }
        except Exception as exc:
            log.warning("ollama_extract_fallback", error=str(exc))
            return {"sender": sender, "subject": subject}

    async def format_whatsapp_alert(
        self,
        sender: str,
        subject: str,
        priority: bool,
        snippet: str,
    ) -> str:
        system = (
            "You write a short WhatsApp notification about a new email. "
            "Respond with ONLY the message text. If priority is true, start with TOP PRIORITY."
        )
        user = f"""priority={priority}
sender={sender}
subject={subject}
snippet={snippet[:400]}

Keep it under 8 lines."""
        try:
            raw = await self._chat(system, user, temperature=0.3)
            text = strip_think_blocks(raw).strip().strip('"')
            if not text:
                raise ValueError("empty formatted alert")
            if priority and "TOP PRIORITY" not in text.upper():
                text = f"TOP PRIORITY\n{text}"
            return text
        except Exception as exc:
            log.warning("ollama_format_fallback", error=str(exc))
            flag = "TOP PRIORITY\n" if priority else ""
            return f"{flag}New email\nFrom: {sender}\nSubject: {subject}".strip()

    async def health(self) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            tags = response.json()
        names = [item.get("name") for item in tags.get("models", [])]
        return {
            "ok": True,
            "base_url": self.base_url,
            "model": self.model,
            "available_models": names,
            "model_present": any(self.model in (name or "") for name in names),
        }
