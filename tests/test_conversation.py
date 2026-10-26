"""
Unit tests for Voice and Conversational engines.
"""

from core.voice_engine import VoiceEngine
from core.conversation_agent import ConversationAgent
from core.resume_parser import ResumeParser


def test_voice_engine_js_generation():
    engine = VoiceEngine()
    js = engine.generate_browser_speech_js("Hello candidate, welcome to the interview.")
    assert "SpeechSynthesisUtterance" in js
    assert "Hello candidate" in js


def test_conversation_agent_offline():
    agent = ConversationAgent(persona_name="Alex (Rigorous Tech Lead)")
    current_q = {
        "question": "How do you handle database race conditions in microservices?",
        "category": "Software Engineering",
        "keywords": ["lock", "redis", "isolation"],
        "expected_concepts": ["Distributed locks", "Optimistic concurrency"]
    }
    nlp_eval = {
        "overall_score": 75.0,
        "star": {"coverage": {"Result": True}},
        "fluency": {"word_count": 45, "filler_count": 0},
        "keywords": {"missing": []}
    }
    reply = agent.generate_response("I used Redis Redlock with atomic Lua scripts to prevent concurrent updates.", current_q, nlp_eval)
    assert len(reply) > 20
    assert isinstance(reply, str)


def test_resume_parser_skills():
    parser = ResumeParser()
    sample_text = """
    Priya Sharma
    Skills: Python, PyTorch, Hugging Face Transformers, spaCy, FastAPI, Docker, PostgreSQL
    - Built a RAG pipeline using vector embeddings and BM25 search.
    - Fine-tuned Llama 3 8B using LoRA for summarization.
    """
    parsed = parser.parse_resume(sample_text)
    assert "Python" in parsed["skills"].get("Languages", [])
    assert "Transformers" in parsed["skills"].get("NLP & AI", []) or "spaCy" in parsed["skills"].get("NLP & AI", [])
    assert len(parsed["experience_points"]) >= 1

    tailored_qs = parser.generate_tailored_questions(parsed)
    assert len(tailored_qs) >= 2
