# Development notes

Problems found while building pr-review-bot, what caused them, and what was done.

## 1. `client.interactions` not found
- **Symptom:** `AttributeError: 'Client' object has no attribute 'interactions'`
- **Likely cause:** The sample code from AI Studio "Get code" used a newer API than the SDK installed on Python 3.9.
- **Fix:** Switched to `client.models.generate_content`, which works with the installed SDK.
- **Status:** Worked around. Upgrading Python (3.11+) and using the newer SDK is still open.

## 2. Request hung, then `504 DEADLINE_EXCEEDED`
- **Symptom:** The script waited with no output, then returned 504 with `gemini-3.8-flash`.
- **Cause:** The request reached the API, but the model did not answer in time. Exact reason unknown.
- **Fix:** Added a request timeout and switched to `gemini-3.1-flash-lite`, which answered normally.
- **Status:** Fixed for now. The model name is configurable with the `REVIEW_MODEL` environment variable.

## 3. `404 NOT_FOUND` for `gemini-2.5-flash`
- **Cause:** That model is no longer available to new users.
- **Fix:** Picked a current model from the list returned by the API.
- **Lesson:** Check the model list from the API instead of assuming a name.

## 4. `Missing key inputs argument`
- **Cause:** `GEMINI_API_KEY` was not set in the terminal that ran the script.
- **Fix:** Load the key from a local `.env` file (ignored by git) with `python-dotenv`.

## 5. Embedded git repository
- **Symptom:** `warning: adding embedded git repository` and a broken folder entry on GitHub.
- **Likely cause:** A second `git init` was created inside the project folder.
- **Fix:** Removed the nested repository and recreated the virtual environment at the project root.

## 6. Prompt padding notes with praise
- **Symptom:** For a diff that was already fine, the model filled the "2 to 3 notes" rule with praise and a repeated point.
- **Cause:** The prompt required at least 2 notes, so the model had to produce something.
- **Fix:** Changed the rule to 1 to 3 notes, each a different concrete concern, no praise, and one "no issues found" note if there is nothing to flag.
- **Status:** Fixed. After the change, the "already fine" sample returned two distinct notes with no praise, and the bug sample still flagged the formula error.

## 7. Known limitation: some notes are slightly inaccurate
- **Examples:** On the bug sample, one note gave the wrong condition for negative prices. On the "already fine" sample, one note described the change as going from returning a value to raising an exception, although the old code also raised an error (a different one).
- **Cause:** The model sees only the diff, not the callers or the full code, and can state details wrongly.
- **Status:** Not fixed. The output should be treated as a hint for a human reviewer, not a verdict. A larger set of sample diffs is planned to check how often this happens.