"""
Computational Linguistics & NLP Analysis Engine for AI Interview Coach.
Combines fluency metrics, STAR evaluation, semantic similarity, keyword matching,
sentiment/tone classification, and readability.
"""

import re
from typing import Dict, List, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.fluency_detector import FluencyDetector
from core.star_evaluator import STAREvaluator

# Optional spaCy integration with lazy loading
_nlp = None

def get_spacy_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        except Exception:
            _nlp = False
    return _nlp if _nlp is not False else None


class NLPAnalyzer:
    def __init__(self):
        self.fluency_detector = FluencyDetector()
        self.star_evaluator = STAREvaluator()

        # Positive & Assertive vocabulary vs Hesitant/Uncertain vocabulary
        self.confident_words = {
            "spearheaded", "architected", "optimized", "implemented", "delivered", "solved",
            "achieved", "championed", "led", "streamlined", "diagnosed", "engineered",
            "benchmark", "proven", "confident", "consistently", "collaborated", "successfully"
        }
        self.hesitant_words = {
            "maybe", "perhaps", "i think", "i guess", "probably", "sort of", "kind of",
            "might have", "not sure", "possibly", "somehow", "hopefully", "tried to"
        }

    def compute_semantic_relevance(self, candidate_answer: str, expected_concepts: List[str], keywords: List[str]) -> float:
        """
        Computes cosine similarity between candidate answer and benchmark rubric concepts.
        """
        if not candidate_answer or not candidate_answer.strip():
            return 0.0

        reference_text = " ".join(expected_concepts + keywords)
        if not reference_text.strip():
            return 50.0

        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
            tfidf_matrix = vectorizer.fit_transform([candidate_answer, reference_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Scale non-linearly to 0-100 range
            return round(min(100.0, float(similarity * 150.0)), 1)
        except Exception:
            return 50.0

    def match_keywords(self, text: str, target_keywords: List[str]) -> Dict[str, Any]:
        """
        Calculates domain keyword coverage between candidate response and target keywords.
        """
        if not target_keywords:
            return {"matched": [], "missing": [], "coverage_pct": 100.0}

        text_lower = text.lower()
        matched = []
        missing = []

        for kw in target_keywords:
            kw_clean = kw.lower().strip()
            # Boundary search or substring
            pattern = rf'\b{re.escape(kw_clean)}\b'
            if re.search(pattern, text_lower) or kw_clean in text_lower:
                matched.append(kw)
            else:
                missing.append(kw)

        coverage = round((len(matched) / max(1, len(target_keywords))) * 100, 1)
        return {
            "matched": matched,
            "missing": missing,
            "coverage_pct": coverage
        }

    def analyze_tone_and_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Evaluates tone, assertiveness, and confidence markers.
        """
        text_lower = text.lower()
        conf_count = sum(1 for w in self.confident_words if w in text_lower)
        hes_count = sum(1 for w in self.hesitant_words if w in text_lower)

        # Baseline confidence is 65
        confidence_score = 65.0 + (conf_count * 6.0) - (hes_count * 8.0)
        confidence_score = max(20.0, min(100.0, round(confidence_score, 1)))

        if confidence_score >= 80:
            tone_label = "Assertive & Confident"
        elif confidence_score >= 60:
            tone_label = "Balanced & Professional"
        else:
            tone_label = "Tentative / Hesitant"

        return {
            "confidence_score": confidence_score,
            "tone_label": tone_label,
            "confident_markers_count": conf_count,
            "hesitation_markers_count": hes_count
        }

    def analyze_comprehensive(
        self,
        answer: str,
        question: Optional[Dict[str, Any]] = None,
        duration_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Full computational linguistics evaluation report for a given answer.
        """
        # 1. Fluency & Readability
        fluency = self.fluency_detector.analyze(answer, duration_seconds)

        # 2. STAR Method Adherence
        star = self.star_evaluator.evaluate(answer)

        # 3. Keyword & Semantic Alignment
        keywords = question.get("keywords", []) if question else []
        expected_concepts = question.get("expected_concepts", []) if question else []

        keyword_analysis = self.match_keywords(answer, keywords)
        semantic_score = self.compute_semantic_relevance(answer, expected_concepts, keywords)

        # 4. Tone & Sentiment
        tone = self.analyze_tone_and_sentiment(answer)

        # 5. Composite Scoring
        # 25% Keyword & Semantic relevance
        # 25% STAR Framework adherence
        # 20% Fluency (low fillers, optimal tempo)
        # 20% Readability & length completeness
        # 10% Tone & Confidence
        keyword_score = keyword_analysis["coverage_pct"] if keywords else 80.0
        star_score = star["star_score"]
        fluency_score = fluency["fluency_score"]
        relevance_score = (semantic_score * 0.5) + (keyword_score * 0.5)

        # Length adequacy bonus/penalty
        words = fluency["word_count"]
        if words < 15:
            length_factor = 0.6
        elif words < 30:
            length_factor = 0.88
        elif words > 450:
            length_factor = 0.92  # slightly too verbose
        else:
            length_factor = 1.0

        raw_overall = (
            relevance_score * 0.30 +
            star_score * 0.25 +
            fluency_score * 0.25 +
            tone["confidence_score"] * 0.20
        ) * length_factor

        overall_score = round(max(10.0, min(100.0, raw_overall)), 1)

        # Actionable synthesis coaching tips
        coaching_summary = []
        if words < 35:
            coaching_summary.append("Your response was very brief. Elaborate with concrete examples, technologies used, and outcomes.")
        if keyword_analysis["missing"] and len(keyword_analysis["missing"]) > 1:
            top_missing = ", ".join(keyword_analysis["missing"][:3])
            coaching_summary.append(f"Consider addressing key domain terminology: **{top_missing}**.")
        if star["feedback"]:
            coaching_summary.extend(star["feedback"])
        if fluency["tips"]:
            coaching_summary.extend(fluency["tips"])

        return {
            "overall_score": overall_score,
            "fluency": fluency,
            "star": star,
            "keywords": keyword_analysis,
            "semantic_score": semantic_score,
            "tone": tone,
            "coaching_summary": list(dict.fromkeys(coaching_summary))[:5]  # deduplicated top 5
        }
