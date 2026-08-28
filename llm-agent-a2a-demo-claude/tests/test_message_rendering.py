"""The WhatsApp text is the user-facing contract: sender, subject, priority flag."""

from mail_a2a.agents.whatsapp_agent import one_line, render_message
from mail_a2a.models import NotifyRequest

REQUEST = NotifyRequest(
    uid="7",
    sender="Priya Raman <priya@example.com>",
    subject="Senior Engineer position",
    priority=True,
    matched_keywords=["position"],
    received_at="2026-08-16T09:12:00+04:00",
)


def test_message_contains_sender_subject_and_priority_flag():
    text = render_message(REQUEST, "A recruiter is asking about your availability.")
    assert "TOP PRIORITY" in text
    assert "Priya Raman <priya@example.com>" in text
    assert "Senior Engineer position" in text
    assert "A recruiter is asking about your availability." in text


def test_priority_flag_lists_matched_keywords():
    assert "(position)" in render_message(REQUEST)


def test_non_priority_message_has_no_flag():
    ordinary = REQUEST.model_copy(update={"priority": False, "matched_keywords": []})
    text = render_message(ordinary)
    assert "TOP PRIORITY" not in text
    assert "Senior Engineer position" in text


def test_message_is_complete_without_any_llm_output():
    # Ollama being down must not cost the user the sender or subject.
    text = render_message(REQUEST, "")
    assert "*From:* Priya Raman <priya@example.com>" in text
    assert "*Subject:* Senior Engineer position" in text
    assert text.rstrip() == text


def test_one_line_keeps_first_sentence_only():
    assert one_line("First thing. Second thing. Third.") == "First thing."


def test_one_line_strips_markdown_and_whitespace():
    assert one_line('  "**A recruiter wrote in**"  ') == "A recruiter wrote in"


def test_one_line_truncates_a_rambling_answer():
    result = one_line(" ".join(["word"] * 60))
    assert result.endswith("…")
    assert len(result.split()) == 24  # MAX_CONTEXT_WORDS, ellipsis glued to the last


def test_one_line_of_nothing_is_empty():
    assert one_line("") == ""
    assert one_line("   ") == ""
