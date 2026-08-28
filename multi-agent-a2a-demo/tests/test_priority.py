from a2a_mail_notify.priority import is_top_priority


KEYWORDS = ["job", "opportunity", "opening", "position"]


def test_priority_matches_whole_word():
    assert is_top_priority("We have a job for you", KEYWORDS)
    assert is_top_priority("Great OPPORTUNITY inside", KEYWORDS)
    assert is_top_priority("New opening on the team", KEYWORDS)
    assert is_top_priority("Open position: backend", KEYWORDS)


def test_priority_ignores_partial_tokens():
    assert not is_top_priority("Please review the invoice", KEYWORDS)
    assert not is_top_priority("Hello from accounting", KEYWORDS)


def test_priority_empty():
    assert not is_top_priority("", KEYWORDS)
    assert not is_top_priority("job opening", [])
