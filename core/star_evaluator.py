"""
STAR Method Adherence Evaluator.
Decomposes answers into sentences and classifies them into Situation, Task, Action, and Result
using our custom trained TF-IDF + Logistic Regression model with linguistic heuristics.
"""

import os
import re
import pickle
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "star_classifier.pkl"

class STAREvaluator:
    def __init__(self):
        self.model = None
        self._load_model()

        # Fallback linguistic indicator patterns if model unavailable
        self.heuristics = {
            "Situation": [r"\bwhen i was\b", r"\bduring my\b", r"\bin my previous\b", r"\bour team was\b", r"\bwe had a problem\b", r"\bthe company\b", r"\bcontext\b"],
            "Task": [r"\bmy goal was\b", r"\bi was assigned\b", r"\bmy responsibility\b", r"\bthe objective\b", r"\bneeded to\b", r"\btasked with\b", r"\bhad to build\b"],
            "Action": [r"\bi built\b", r"\bi implemented\b", r"\bi designed\b", r"\bi profiled\b", r"\bi organized\b", r"\bi configured\b", r"\bi wrote\b", r"\bi refactored\b", r"\bi developed\b"],
            "Result": [r"\bas a result\b", r"\bultimately\b", r"\breduced by\b", r"\bincreased by\b", r"\bimproved\b", r"\bsaved\b", r"\boutcome was\b", r"\bhelped achieve\b", r"%", r"\$\d+"]
        }

    def _load_model(self):
        if MODEL_PATH.exists():
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
            except Exception as e:
                print(f"[Warning] Could not load STAR classifier model: {e}")
                self.model = None

    def _rule_based_tag(self, sentence: str) -> str:
        tags = self._rule_based_tags(sentence)
        return tags[0] if tags else "General"

    def _rule_based_tags(self, sentence: str) -> List[str]:
        s_lower = sentence.lower()
        return [
            tag for tag, patterns in self.heuristics.items()
            if any(re.search(pat, s_lower) for pat in patterns)
        ]

    def evaluate(self, answer_text: str) -> Dict[str, Any]:
        """
        Evaluates interview answer text for STAR component coverage and quality.
        """
        if not answer_text or not answer_text.strip():
            return {
                "star_score": 0.0,
                "coverage": {"Situation": False, "Task": False, "Action": False, "Result": False},
                "tagged_sentences": [],
                "feedback": ["No response recorded."],
                "breakdown": {"Situation": 0, "Task": 0, "Action": 0, "Result": 0, "General": 0}
            }

        # Split sentences
        raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', answer_text) if s.strip()]
        if not raw_sentences:
            raw_sentences = [answer_text.strip()]

        tagged_sentences = []
        breakdown = {"Situation": 0, "Task": 0, "Action": 0, "Result": 0, "General": 0}

        for sent in raw_sentences:
            tag = "General"
            conf = 0.5
            tags = self._rule_based_tags(sent)
            if self.model:
                try:
                    probs = self.model.predict_proba([sent])[0]
                    classes = self.model.classes_
                    best_idx = probs.argmax()
                    tag = classes[best_idx]
                    conf = round(float(probs[best_idx]), 2)
                    if tag in self.heuristics and tag not in tags:
                        tags.append(tag)
                    if not tags and tag in self.heuristics:
                        tags = [tag]
                except Exception:
                    tag = tags[0] if tags else "General"
            if not tags and tag in self.heuristics:
                tags = [tag]
            if not tags:
                tags = ["General"]
            if tag not in tags:
                tag = tags[0]
            for component in tags:
                breakdown[component] = breakdown.get(component, 0) + 1
            tagged_sentences.append({
                "sentence": sent,
                "tag": tag,
                "tags": tags,
                "confidence": conf
            })

        # Calculate coverage
        coverage = {
            "Situation": breakdown["Situation"] > 0,
            "Task": breakdown["Task"] > 0,
            "Action": breakdown["Action"] > 0,
            "Result": breakdown["Result"] > 0
        }

        # STAR Scoring
        # Action and Result are highest weight in behavioral assessments
        weights = {"Situation": 20, "Task": 20, "Action": 35, "Result": 25}
        total_score = sum(weights[comp] for comp, present in coverage.items() if present)

        # Bonus for well-elaborated actions and quantifiable results
        action_bonus = min(10, breakdown["Action"] * 3) if coverage["Action"] else 0
        result_metric_bonus = 10 if (coverage["Result"] and any(re.search(r'(\d+%|\$\d+|\d+x|\d+ seconds|\d+ms)', s["sentence"]) for s in tagged_sentences if "Result" in s["tags"])) else 0

        final_star_score = min(100.0, float(total_score + action_bonus + result_metric_bonus))

        # Feedback generation
        feedback = []
        if not coverage["Situation"]:
            feedback.append("Missing **Situation**: Clearly state the background context, company, or constraint.")
        if not coverage["Task"]:
            feedback.append("Missing **Task**: Specify your personal assignment or the primary objective.")
        if not coverage["Action"]:
            feedback.append("Missing **Action**: Describe concrete steps, technical decisions, or tools you spearheaded.")
        if not coverage["Result"]:
            feedback.append("Missing **Result**: Quantify outcomes with metrics (e.g., % improvement, latency reduced, revenue saved).")
        elif result_metric_bonus == 0:
            feedback.append("Tip for **Result**: Include quantifiable numbers (e.g. 'reduced latency by 40%', 'saved 10 hours/week').")

        if all(coverage.values()):
            feedback.append("Strong STAR structure! All four components (Situation, Task, Action, Result) were addressed.")

        return {
            "star_score": round(final_star_score, 1),
            "coverage": coverage,
            "tagged_sentences": tagged_sentences,
            "feedback": feedback,
            "breakdown": breakdown
        }
