"""
Unit tests for NLP and Computational Linguistics engines.
"""

import pytest
from core.fluency_detector import FluencyDetector
from core.star_evaluator import STAREvaluator
from core.nlp_analyzer import NLPAnalyzer


def test_fluency_detector_filler_words():
    detector = FluencyDetector()
    sample = "Um, I think, like, we basically optimized the database query, you know?"
    res = detector.analyze(sample, duration_seconds=10.0)

    assert res["filler_count"] >= 3
    assert "um" in res["filler_breakdown"]
    assert "like" in res["filler_breakdown"]
    assert res["word_count"] > 5
    assert 0.0 < res["lexical_diversity"] <= 1.0


def test_star_evaluator_components():
    evaluator = STAREvaluator()
    sample = (
        "In my previous company, our checkout API experienced high latency. "
        "My goal was to reduce response times below 100 milliseconds. "
        "I implemented Redis caching and optimized PostgreSQL indexes. "
        "As a result, API latency dropped by 65% and cart abandons decreased."
    )
    res = evaluator.evaluate(sample)

    assert res["star_score"] >= 75.0
    assert res["coverage"]["Situation"] is True
    assert res["coverage"]["Task"] is True
    assert res["coverage"]["Action"] is True
    assert res["coverage"]["Result"] is True


def test_nlp_analyzer_comprehensive():
    analyzer = NLPAnalyzer()
    question = {
        "question": "How do you optimize slow database queries?",
        "keywords": ["index", "caching", "redis", "query", "postgresql", "latency"],
        "expected_concepts": ["Indexing on frequently filtered columns", "Distributed caching", "Query plan analysis"]
    }
    answer = (
        "When our PostgreSQL query latency spiked, I profiled the execution plan with EXPLAIN ANALYZE. "
        "I added composite B-Tree indexes on the user_id column and introduced Redis caching. "
        "This reduced query times by 80% and stabilized the application."
    )
    res = analyzer.analyze_comprehensive(answer, question=question, duration_seconds=15.0)

    assert res["overall_score"] >= 65.0
    assert len(res["keywords"]["matched"]) >= 2
    assert res["fluency"]["word_count"] > 20
    assert len(res["coaching_summary"]) > 0
    assert res["tone"]["interpretation_note"].startswith("Text-only")
    assert res["fluency"]["estimated_wpm"] == round(
        res["fluency"]["word_count"] / 15.0 * 60, 1
    )


def test_text_only_analysis_does_not_invent_speaking_rate_or_overall_score():
    result = NLPAnalyzer().analyze_comprehensive("I worked with the team and shipped the service.")
    assert result["fluency"]["estimated_wpm"] is None
    assert result["overall_score"] is None
    assert result["score_components"] == {}
