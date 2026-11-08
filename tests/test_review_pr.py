from review_pr import format_comment


def test_format_comment_contains_summary_and_notes():
    text = format_comment({"summary": "Does X.", "notes": ["a", "b"]})
    assert "Does X." in text
    assert "- a" in text and "- b" in text


def test_format_comment_mentions_truncation():
    text = format_comment({"summary": "s", "notes": ["a"]}, truncated=True)
    assert "cut before review" in text