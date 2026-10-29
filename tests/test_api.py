"""
Unit and integration tests for FastAPI backend functions.
"""

from server import (
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

def test_health_check_function():
    data = health_check()
    assert data["status"] == "healthy"
    assert data["ai_autofetch_active"] is True
    assert data["total_questions"] >= 200

def test_personas_function():
    personas = get_personas()
    assert "Dr. Maya (NLP & Computational Linguistics Expert)" in personas
    assert "Alex (Rigorous Tech Lead)" in personas

def test_questions_function():
    qs = get_questions(limit=5)
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
    assert res["overall_score"] >= 65.0
    assert res["star"]["coverage"]["Result"] is True
    assert "linguistics" in res
    assert res["linguistics"]["flesch_reading_ease"] > 0

def test_chat_with_interviewer_function():
    req = ChatRequest(
        persona_name="Dr. Maya (NLP & Computational Linguistics Expert)",
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
