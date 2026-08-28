import httpx
import pytest

from mail_a2a.config import OllamaSettings
from mail_a2a.llm.ollama import OllamaClient, OllamaUnavailable, strip_reasoning


def test_strip_reasoning_removes_think_block():
    raw = "<think>Let me consider this carefully.</think>\n\nThe answer."
    assert strip_reasoning(raw) == "The answer."


def test_strip_reasoning_handles_truncated_block():
    # A response cut off by num_predict leaves <think> unclosed.
    assert strip_reasoning("Prefix. <think>still reasoning and then cut") == "Prefix."


def test_strip_reasoning_passes_plain_text_through():
    assert strip_reasoning("  just an answer  ") == "just an answer"


@pytest.fixture
def mock_transport(monkeypatch):
    def install(handler):
        transport = httpx.MockTransport(handler)
        original_init = httpx.AsyncClient.__init__

        def patched_init(self, *args, **kwargs):
            kwargs["transport"] = transport
            original_init(self, *args, **kwargs)

        monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)

    return install


async def test_chat_strips_reasoning_and_sends_think_false(mock_transport):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        seen.update(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "message": {"content": "<think>hmm</think>A recruiter wants a call."},
                "eval_count": 42,
                "done_reason": "stop",
            },
        )

    mock_transport(handler)
    answer = await OllamaClient(OllamaSettings(), agent="t").chat("sys", "user")
    assert answer == "A recruiter wants a call."
    assert seen["think"] is False
    assert seen["stream"] is False


async def test_chat_json_recovers_object_from_code_fence(mock_transport):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "message": {
                    "content": '```json\n{"summary": "Job opening", "job_related": true}\n```'
                }
            },
        )

    mock_transport(handler)
    parsed = await OllamaClient(OllamaSettings(), agent="t").chat_json("sys", "user")
    assert parsed == {"summary": "Job opening", "job_related": True}


async def test_chat_returns_empty_when_ollama_is_down(mock_transport):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    mock_transport(handler)
    # required=False: notifications must survive an unavailable model.
    assert await OllamaClient(OllamaSettings(), agent="t").chat("sys", "user") == ""


async def test_chat_raises_when_model_is_required(mock_transport):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    mock_transport(handler)
    client = OllamaClient(OllamaSettings(required=True), agent="t")
    with pytest.raises(OllamaUnavailable):
        await client.chat("sys", "user")
