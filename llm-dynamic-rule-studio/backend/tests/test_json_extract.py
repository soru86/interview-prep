from app.services.json_extract import extract_json_object, strip_think_blocks


def test_strip_think_blocks():
    assert strip_think_blocks("<think>reason</think>{\"ok\":true}") == '{"ok":true}'


def test_extract_json_with_fence():
    raw = """<think>planning</think>
```json
{"name": "VIP Rule", "description": "x"}
```"""
    data = extract_json_object(raw)
    assert data["name"] == "VIP Rule"
