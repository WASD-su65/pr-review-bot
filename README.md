# pr-review-bot

A small Python service that asks an LLM (Google Gemini API) to summarize a pull request diff and point out possible issues. The model is asked to reply in a fixed JSON shape, and the code validates the reply and retries once if it is malformed.

Status: work in progress.

## What works now
- `reviewer.py`: `summarize_diff(diff)` sends a git diff to the model and returns `{"summary": ..., "notes": [...]}`
- Output validation (valid JSON, required fields, 1 to 3 notes) with one automatic retry
- Unit tests that run without calling the real API (`pytest`)

## Run it
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "GEMINI_API_KEY=your-key" > .env
python try_call.py samples/diff1.diff
python -m pytest -q
```

## Not done yet
- HTTP service (`/health`, `/review`)
- Docker image and Kubernetes (minikube) deployment
- Running automatically on pull requests
- A larger set of sample diffs to evaluate prompt changes

## Notes
- The API key is read from the environment or a local `.env` file, which is not committed.
- Sample diffs are short and written for testing only.