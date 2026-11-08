import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = os.environ.get("REVIEW_MODEL", "gemini-3.1-flash-lite")

SYSTEM_INSTRUCTION = """You are an assistant that helps engineers review pull requests.
Given a git diff, respond ONLY with a JSON object in this exact shape:
{"summary": "<one or two sentences describing the change>", "notes": ["<observation 1>", "<observation 2>"]}
Rules:
- "notes" has 2 to 3 short items about possible bugs, missing tests, or unclear code.
- Comment only on lines that changed in the diff.
- Do not invent problems. If the diff looks fine, say so in "notes".
- Do not include any text outside the JSON."""


class ReviewError(Exception):
    pass


def _clean(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return text.strip()


def parse_review(text: str) -> dict:
    """Turn the model's text into a validated dict, or raise ReviewError."""
    try:
        data = json.loads(_clean(text))
    except json.JSONDecodeError as e:
        raise ReviewError(f"not valid JSON: {e}")
    if not isinstance(data, dict):
        raise ReviewError("JSON is not an object")
    summary = data.get("summary")
    notes = data.get("notes")
    if not isinstance(summary, str) or not summary.strip():
        raise ReviewError("missing or empty 'summary'")
    if not isinstance(notes, list) or not (1 <= len(notes) <= 3):
        raise ReviewError("'notes' must be a list of 1 to 3 items")
    if not all(isinstance(n, str) and n.strip() for n in notes):
        raise ReviewError("every note must be a non-empty string")
    return {"summary": summary.strip(), "notes": [n.strip() for n in notes]}


def summarize_diff(diff: str, retries: int = 1) -> dict:
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
        http_options=types.HttpOptions(timeout=60000),
    )
    last_error = None
    for _ in range(retries + 1):
        response = client.models.generate_content(
            model=MODEL,
            contents=diff,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
        )
        try:
            return parse_review(response.text or "")
        except ReviewError as e:
            last_error = e
    raise ReviewError(f"model output rejected after {retries + 1} attempts: {last_error}")