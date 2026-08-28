import pytest

from mail_a2a.priority import evaluate, match_keywords

KEYWORDS = ["job", "opportunity", "opening", "position"]


@pytest.mark.parametrize(
    "subject,expected",
    [
        ("Senior Engineer position at Acme", ["position"]),
        ("New opening on the platform team", ["opening"]),
        ("An opportunity you might like", ["opportunity"]),
        ("Job alert: 5 new matches", ["job"]),
        ("Your invoice is ready", []),
    ],
)
def test_subject_keywords(subject, expected):
    is_priority, matched = evaluate(subject, "", KEYWORDS)
    assert matched == expected
    assert is_priority is bool(expected)


def test_body_alone_triggers_priority():
    is_priority, matched = evaluate("Quick question", "We have an opening on my team.", KEYWORDS)
    assert is_priority
    assert matched == ["opening"]


def test_matching_is_case_insensitive():
    assert match_keywords("JOB OPPORTUNITY", KEYWORDS) == ["job", "opportunity"]


def test_plurals_and_possessives_match():
    assert match_keywords("two openings and three positions", KEYWORDS) == ["opening", "position"]


@pytest.mark.parametrize("text", ["repositioning the brand", "jobless claims", "reopening soon"])
def test_substrings_do_not_match(text):
    # \b anchors keep 'position' out of 'repositioning'.
    assert match_keywords(text, KEYWORDS) == []


def test_results_follow_config_order_without_duplicates():
    matched = match_keywords("position, job, position, opening", KEYWORDS)
    assert matched == ["job", "opening", "position"]


def test_custom_keywords_from_config():
    assert match_keywords("Invoice overdue", ["invoice"]) == ["invoice"]
    assert match_keywords("Invoice overdue", KEYWORDS) == []


def test_empty_inputs_are_safe():
    assert evaluate("", "", KEYWORDS) == (False, [])
    assert match_keywords("anything", []) == []
