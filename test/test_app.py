from fastapi.testclient import TestClient

import app as app_module
from reviewer import ReviewError

client = TestClient(app_module.app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_review_returns_model_result(monkeypatch):
    fake = {"summary": "ok", "notes": ["a", "b"]}
    monkeypatch.setattr(app_module, "summarize_diff", lambda diff: fake)
    response = client.post("/review", json={"diff": "some diff"})
    assert response.status_code == 200
    assert response.json() == fake


def test_review_rejects_empty_diff():
    response = client.post("/review", json={"diff": "   "})
    assert response.status_code == 400


def test_review_rejects_huge_diff():
    response = client.post("/review", json={"diff": "x" * 100_001})
    assert response.status_code == 413


def test_review_returns_502_when_model_output_invalid(monkeypatch):
    def boom(diff):
        raise ReviewError("bad output")

    monkeypatch.setattr(app_module, "summarize_diff", boom)
    response = client.post("/review", json={"diff": "some diff"})
    assert response.status_code == 502