import pytest

from app.ai.analyzer import clean_json_response


def test_plain_json():
    text = '{"category": "Sales", "priority": "HIGH"}'

    result = clean_json_response(text)

    assert result == text


def test_json_code_fence():
    text = """```json
{"category": "Sales", "priority": "HIGH"}
```"""

    result = clean_json_response(text)

    assert result == '{"category": "Sales", "priority": "HIGH"}'


def test_plain_code_fence():
    text = """```
{"category": "Sales", "priority": "HIGH"}
```"""

    result = clean_json_response(text)

    assert result == '{"category": "Sales", "priority": "HIGH"}'


def test_extra_text_around_json():
    text = """Here is the result:
{"category": "Sales", "priority": "HIGH"}
Thank you."""

    result = clean_json_response(text)

    assert result == '{"category": "Sales", "priority": "HIGH"}'


def test_whitespace_is_removed():
    text = '   {"category": "Sales", "priority": "HIGH"}   '

    result = clean_json_response(text)

    assert result == '{"category": "Sales", "priority": "HIGH"}'


def test_invalid_response_without_json():
    text = "Gemini could not analyze this email."

    result = clean_json_response(text)

    assert result == text