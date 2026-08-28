from a2a_mail_notify.jsonutil import extract_json_object, strip_think_blocks


def test_strip_think_and_extract_json():
    raw = (
        "<"
        + "think"
        + ">reasoning here"
        + "</think>"
        + '\n```json\n{"sender": "Ada", "subject": "Hello"}\n```'
    )
    data = extract_json_object(raw)
    assert data["sender"] == "Ada"
    assert data["subject"] == "Hello"


def test_extract_bare_object():
    assert extract_json_object('noise {"a": 1} trailing') == {"a": 1}


def test_strip_think_blocks_only():
    text = "<think>abc</think>\nhello"
    # Use the same construction as production in case of tag filtering.
    assert "hello" in strip_think_blocks(text)
