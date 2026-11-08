from fastapi import FastAPI, HTTPException
from google.genai import errors as genai_errors
from pydantic import BaseModel

from reviewer import ReviewError, summarize_diff

MAX_DIFF_CHARS = 100_000

app = FastAPI(title="pr-review-bot")


class ReviewRequest(BaseModel):
    diff: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/review")
def review(request: ReviewRequest):
    if not request.diff.strip():
        raise HTTPException(status_code=400, detail="diff is empty")
    if len(request.diff) > MAX_DIFF_CHARS:
        raise HTTPException(status_code=413, detail="diff is too large")
    try:
        return summarize_diff(request.diff)
    except ReviewError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except genai_errors.APIError as e:
        raise HTTPException(status_code=502, detail=f"model API error: {e}")