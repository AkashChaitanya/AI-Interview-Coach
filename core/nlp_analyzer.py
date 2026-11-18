"""
Computational Linguistics & NLP Analysis Engine for AI Interview Coach.
Combines fluency metrics, STAR evaluation, semantic similarity, keyword matching,
sentiment/tone classification, and readability.
"""

import re
from collections import Counter
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
            _nlp = spacy.load("en_core_web_sm")
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

    def compute_semantic_relevance(self, candidate_answer: str, expected_concepts: List[str], keywords: List[str]) -> Optional[float]:
        """
        Computes lexical TF-IDF similarity; this is not an embedding-based semantic score.
        """
        if not candidate_answer or not candidate_answer.strip():
            return 0.0

        reference_text = " ".join(expected_concepts + keywords)
        if not reference_text.strip():
            return None

        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
            tfidf_matrix = vectorizer.fit_transform([candidate_answer, reference_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(float(similarity) * 100.0, 1)
        except ValueError:
            return 0.0

    def match_keywords(self, text: str, target_keywords: List[str]) -> Dict[str, Any]:
        """
        Calculates domain keyword coverage between candidate response and target keywords.
        """
        if not target_keywords:
            return {"matched": [], "missing": [], "coverage_pct": None}

        text_lower = text.lower()
        matched = []
        missing = []

        for kw in target_keywords:
            kw_clean = kw.lower().strip()
            variants = []
            for term in kw_clean.split():
                escaped = re.escape(term)
                if term.endswith("e") and len(term) > 3:
                    stem = re.escape(term[:-1])
                    variants.append(rf"(?:{escaped}|{stem}(?:ing|ed|es|s)?)")
                elif term.endswith("y") and len(term) > 3:
                    stem = re.escape(term[:-1])
                    variants.append(rf"(?:{escaped}|{stem}ies)")
                else:
                    variants.append(rf"{escaped}(?:s|es|ed|ing)?")
            pattern = r"\b" + r"\s+".join(variants) + r"\b"
            if re.search(pattern, text_lower):
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
        Counts directness and hedging markers; these are linguistic observations,
        not measures of psychological confidence or emotional state.
        """
        text_lower = text.lower()
        conf_count = sum(
            len(re.findall(rf"\b{re.escape(marker)}\b", text_lower))
            for marker in self.confident_words
        )
        hes_count = sum(
            len(re.findall(rf"\b{re.escape(marker)}\b", text_lower))
            for marker in self.hesitant_words
        )
        if conf_count > hes_count:
            tone_label = "More direct phrasing markers"
        elif hes_count > conf_count:
            tone_label = "More hedging phrasing markers"
        else:
            tone_label = "Balanced phrasing markers"

        return {
            "tone_label": tone_label,
            "directness_marker_count": conf_count,
            "hedging_marker_count": hes_count,
            "interpretation_note": "Text-only language markers; not a psychological confidence or emotion assessment."
        }

    @staticmethod
    def _clarity_score(text: str, fluency: Dict[str, Any]) -> float:
        word_count = fluency["word_count"]
        sentence_count = fluency["sentence_count"]
        if not word_count:
            return 0.0
        average_length = word_count / max(sentence_count, 1)
        length_score = 100.0 if 8 <= average_length <= 25 else 70.0 if 5 <= average_length <= 35 else 40.0
        transitions = len(re.findall(
            r"\b(first|then|because|therefore|however|finally|as a result|for example)\b",
            text.lower()
        ))
        transition_score = min(20.0, transitions * 5.0)
        return round(min(100.0, length_score * 0.8 + transition_score), 1)

    @staticmethod
    def _linguistic_features(text: str) -> Dict[str, Any]:
        tokens = re.findall(r"\b[\w'-]+\b", text.lower())
        bigrams = [" ".join(tokens[i:i + 2]) for i in range(max(0, len(tokens) - 1))]
        features: Dict[str, Any] = {
            "token_count": len(tokens),
            "bigram_count": len(set(bigrams)),
            "top_bigrams": [
                {"ngram": ngram, "count": count}
                for ngram, count in Counter(bigrams).most_common(10)
            ]
        }
        nlp = get_spacy_nlp()
        if nlp is not None and text.strip():
            doc = nlp(text)
            features.update({
                "lemmas": [token.lemma_ for token in doc if not token.is_space][:200],
                "pos_counts": {
                    pos: sum(1 for token in doc if token.pos_ == pos)
                    for pos in sorted({token.pos_ for token in doc if token.pos_})
                },
                "named_entities": [
                    {"text": entity.text, "label": entity.label_}
                    for entity in doc.ents[:50]
                ]
            })
        else:
            features["spacy_model_available"] = False
        return features

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

        # 4. Observable language markers and clarity
        tone = self.analyze_tone_and_sentiment(answer)
        clarity_score = self._clarity_score(answer, fluency)

        # Scores are only produced when a question rubric is present.
        keyword_score = keyword_analysis["coverage_pct"]
        relevance_parts = []
        if semantic_score is not None:
            relevance_parts.append((semantic_score, 0.6 if keyword_score is not None else 1.0))
        if keyword_score is not None:
            relevance_parts.append((keyword_score, 0.4 if semantic_score is not None else 1.0))
        relevance_score = (
            round(sum(value * weight for value, weight in relevance_parts) /
                  sum(weight for _, weight in relevance_parts), 1)
            if relevance_parts else None
        )
        is_behavioral = bool(question and any(
            term in str(question.get("category", "")).lower()
            for term in ("behavioral", "hr", "leadership")
        ))
        score_components: Dict[str, float] = {}
        if relevance_score is not None:
            score_components["answer_relevance"] = relevance_score
        if is_behavioral:
            score_components["star_structure"] = star["star_score"]
        if score_components:
            score_components["fluency_markers"] = fluency["fluency_score"]
            score_components["communication_clarity"] = clarity_score
            weights = (
                {"answer_relevance": 0.35, "star_structure": 0.25,
                 "fluency_markers": 0.2, "communication_clarity": 0.2}
                if is_behavioral else
                {"answer_relevance": 0.55, "fluency_markers": 0.2,
                 "communication_clarity": 0.25}
            )
            active_weights = {
                key: value for key, value in weights.items() if key in score_components
            }
            weight_total = sum(active_weights.values())
            overall_score = round(
                sum(score_components[key] * weight for key, weight in active_weights.items()) /
                weight_total,
                1
            )
        else:
            overall_score = None

        # Actionable synthesis coaching tips
        coaching_summary = []
        words = fluency["word_count"]
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
            "score_components": score_components,
            "score_method": (
                "Question-rubric score: relevance/STAR (behavioral only), transcript fluency markers, and sentence/discourse clarity."
                if overall_score is not None else
                "No overall score: supply a question with keywords or expected concepts to establish an evaluation rubric."
            ),
            "fluency": fluency,
            "star": star,
            "keywords": keyword_analysis,
            "lexical_similarity_score": semantic_score,
            "tone": tone,
            "communication_clarity_score": clarity_score,
            "linguistic_features": self._linguistic_features(answer),
            "linguistics": {
                "flesch_reading_ease": fluency.get("flesch_reading_ease", 0.0),
                "gunning_fog_index": fluency.get("gunning_fog_index", 0.0),
                "lexical_diversity_ttr": fluency.get("lexical_diversity", 0.0),
                "hapax_legomena_ratio": fluency.get("hapax_legomena_ratio", 0.0),
                "avg_sentence_length": fluency.get("avg_sentence_length", 0.0),
                "filler_ratio": fluency.get("filler_percentage", 0.0),
                "lexical_similarity_score": semantic_score
            },
            "coaching_summary": list(dict.fromkeys(coaching_summary))[:5]  # deduplicated top 5
        }
