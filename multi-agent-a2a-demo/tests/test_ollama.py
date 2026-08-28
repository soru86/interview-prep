import pytest

from a2a_mail_notify.llm.ollama import OllamaClient


@pytest.mark.asyncio
async def test_extract_fields_parses_json(httpx_mock):
    think = "<" + "think" + ">x" + "</think>"
    httpx_mock.add_response(
        url="http://localhost:11434/api/chat",
        json={"message": {"content": think + '\n{"sender": "Ada", "subject": "Hi"}'}},
    )
    client = OllamaClient("http://localhost:11434", "deepseek-r1:1.5b", timeout_seconds=5)
    data = await client.extract_email_fields("raw sender", "raw subject", "body")
    assert data["sender"] == "Ada"
    assert data["subject"] == "Hi"


@pytest.mark.asyncio
async def test_health(httpx_mock):
    httpx_mock.add_response(
        url="http://localhost:11434/api/tags",
        json={"models": [{"name": "deepseek-r1:1.5b"}]},
    )
    client = OllamaClient("http://localhost:11434", "deepseek-r1:1.5b")
    health = await client.health()
    assert health["ok"] is True
    assert health["model_present"] is True
