import pytest

import reviewer
from reviewer import ReviewError, parse_review, summarize_diff

GOOD = '{"summary": "Adds an empty check.", "notes": ["Returns 0 for empty input.", "No tests added."]}'


def test_parse_valid_json():
    result = parse_review(GOOD)
    assert result["summary"] == "Adds an empty check."
    assert len(result["notes"]) == 2


def test_parse_accepts_json_inside_code_fence():
    fenced = "```json\n" + GOOD + "\n```"
    assert parse_review(fenced)["summary"] == "Adds an empty check."


def test_parse_rejects_non_json():
    with pytest.raises(ReviewError):
        parse_review("Sure! Here is my review.")


def test_parse_rejects_missing_summary():
    with pytest.raises(ReviewError):
        parse_review('{"notes": ["a"]}')


def test_parse_rejects_too_many_notes():
    with pytest.raises(ReviewError):
        parse_review('{"summary": "x", "notes": ["a", "b", "c", "d"]}')


def test_parse_rejects_empty_notes():
    with pytest.raises(ReviewError):
        parse_review('{"summary": "x", "notes": []}')


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeClient:
    def __init__(self, texts):
        self.texts = list(texts)
        self.calls = 0
        self.models = self

    def generate_content(self, **kwargs):
        text = self.texts[self.calls]
        self.calls += 1
        return FakeResponse(text)


def test_summarize_retries_once_on_bad_output(monkeypatch):
    client = FakeClient(["not json", GOOD])
    monkeypatch.setattr(reviewer.genai, "Client", lambda **kwargs: client)
    result = summarize_diff("some diff")
    assert result["summary"] == "Adds an empty check."
    assert client.calls == 2


def test_summarize_raises_when_all_attempts_fail(monkeypatch):
    client = FakeClient(["bad", "still bad"])
    monkeypatch.setattr(reviewer.genai, "Client", lambda **kwargs: client)
    with pytest.raises(ReviewError):
        summarize_diff("some diff")