"""
Unit and integration tests for FastAPI backend functions.
"""

from uuid import uuid4

from fastapi.testclient import TestClient

import server as server_module
from core.session_store import SessionStore
from server import (
    app,
    health_check,
    get_personas,
    get_questions,
    evaluate_answer,
    chat_with_interviewer,
    nlp_playground,
    EvaluateRequest,
    ChatRequest,
    PlaygroundRequest
)

client = TestClient(app)

def test_health_check_function():
    data = health_check()
    assert data["status"] == "healthy"
    assert "ai_autofetch_active" in data
    assert data["offline_feedback_available"] is True
    assert data["total_questions"] >= 200

def test_personas_function():
    personas = get_personas()
    assert "Dr. Maya (NLP & Computational Linguistics Expert)" in personas
    assert "Alex (Rigorous Tech Lead)" in personas

def test_questions_function():
    qs = get_questions(category=None, difficulty=None, search=None, limit=5, sample_size=3)
    assert len(qs) == 5
    assert "question" in qs[0]
    assert "keywords" in qs[0]

def test_evaluate_answer_function():
    req = EvaluateRequest(
        answer="In our payment processing microservice, we experienced severe latency bottlenecks during peak checkout. My goal was to reduce p99 response times below 100 milliseconds. I deployed composite B-Tree indexes on PostgreSQL and integrated an asynchronous Celery queue with Redis. As a result, API latency dropped by 64% and shopping cart abandonment decreased by 22%.",
        question={
            "question": "How do you optimize slow APIs?",
            "keywords": ["latency", "index", "queue", "cache"],
            "expected_concepts": ["Database optimization", "Asynchronous task queue"]
        },
        duration_seconds=15.0
    )
    res = evaluate_answer(req)
    assert res["overall_score"] is not None
    assert res["score_components"]["answer_relevance"] < 100
    assert res["star"]["coverage"]["Result"] is True
    assert "linguistics" in res
    assert res["linguistics"]["flesch_reading_ease"] > 0

def test_chat_with_interviewer_function():
    req = ChatRequest(
        persona_name="Dr. Maya (NLP & Computational Linguistics Expert)",
        preferred_model="offline",
        candidate_answer="I utilized Byte Pair Encoding subword tokenization and trained transformer attention embeddings.",
        current_question={
            "question": "Explain subword tokenization in NLP.",
            "category": "Computational Linguistics & NLP",
            "keywords": ["bpe", "subword", "vocabulary"],
            "expected_concepts": ["Byte pair encoding", "Out of vocabulary handling"]
        },
        nlp_evaluation={
            "overall_score": 82.0,
            "star": {"coverage": {"Result": True}},
            "fluency": {"word_count": 25, "filler_count": 0},
            "keywords": {"missing": []}
        }
    )
    res = chat_with_interviewer(req)
    assert "acknowledgment" in res
    assert "follow_up_question" in res
    assert "model_exemplar_answer" in res
    assert "provider_used" in res

def test_nlp_playground_function():
    req = PlaygroundRequest(text="We designed a dependency syntax parser using PyTorch with 92% accuracy.")
    res = nlp_playground(req)
    assert "linguistics" in res
    assert res["linguistics"]["lexical_diversity_ttr"] > 0


def test_resume_endpoint_validates_file_type_and_omits_raw_text():
    rejected = client.post(
        "/api/resume/parse",
        files={"file": ("resume.exe", b"not allowed", "application/octet-stream")}
    )
    assert rejected.status_code == 415

    content = b"Skills: Python, FastAPI\n- Built an API service for internal teams."
    accepted = client.post(
        "/api/resume/parse",
        files={"file": ("resume.txt", content, "text/plain")},
        data={"job_description": "Python FastAPI Kubernetes role"}
    )
    assert accepted.status_code == 200
    result = accepted.json()
    assert "raw_text_preview" not in result
    assert result["job_match"]["missing_skills"] == ["Kubernetes"]


def test_resume_endpoint_returns_safe_error_for_malformed_pdf():
    response = client.post(
        "/api/resume/parse",
        files={"file": ("resume.pdf", b"%PDF-not-valid", "application/pdf")}
    )
    assert response.status_code == 400
    assert "malformed" in response.json()["detail"].lower()


def test_session_endpoints_round_trip_and_delete(tmp_path, monkeypatch):
    store = SessionStore(tmp_path / "interviews.sqlite3")
    monkeypatch.setattr(server_module, "session_store", store)
    session_id = str(uuid4())
    payload = {
        "candidate_name": "Test Candidate",
        "persona_name": "Alex",
        "session_data": {
            "active_questions": [{"question": "Tell me about a project."}],
            "current_q_index": 1,
            "session_results": [{"answer": "I delivered the project."}]
        }
    }

    saved = client.put(f"/api/sessions/{session_id}", json=payload)
    assert saved.status_code == 200
    assert saved.json()["question_count"] == 1

    listed = client.get("/api/sessions")
    assert listed.status_code == 200
    assert listed.json()[0]["session_id"] == session_id

    restored = client.get(f"/api/sessions/{session_id}")
    assert restored.status_code == 200
    assert restored.json()["session_data"] == payload["session_data"]

    deleted = client.delete(f"/api/sessions/{session_id}")
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] is True
    assert client.get(f"/api/sessions/{session_id}").status_code == 404


def test_session_endpoints_reject_invalid_ids_and_oversized_data(tmp_path, monkeypatch):
    monkeypatch.setattr(server_module, "session_store", SessionStore(tmp_path / "interviews.sqlite3"))

    invalid_id = client.get("/api/sessions/not-a-uuid")
    assert invalid_id.status_code == 400

    oversized_payload = {
        "candidate_name": "Candidate",
        "persona_name": "Alex",
        "session_data": {"session_results": [], "text": "x" * (2 * 1024 * 1024)}
    }
    oversized = client.put(f"/api/sessions/{uuid4()}", json=oversized_payload)
    assert oversized.status_code == 413
