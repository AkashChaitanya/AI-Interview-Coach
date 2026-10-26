"""
Fluency and Linguistic Metrics Detector.
Analyzes filler words, speech tempo (WPM), lexical diversity (Type-Token Ratio),
and readability for computational linguistics evaluation.
"""

import re
import math
from typing import Dict, List, Any
import config

class FluencyDetector:
    def __init__(self, filler_words: List[str] = None):
        self.filler_words = filler_words or config.FILLER_WORDS
        # Sort fillers by length descending so multi-word fillers like 'you know' are matched first
        self.sorted_fillers = sorted(self.filler_words, key=lambda x: len(x), reverse=True)

    def count_syllables(self, word: str) -> int:
        """Heuristic syllable counter for readability metrics."""
        word = word.lower().strip(".:;?!")
        if not word:
            return 0
        if len(word) <= 3:
            return 1
        word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
        word = re.sub(r'^y', '', word)
        matches = re.findall(r'[aeiouy]{1,2}', word)
        return max(1, len(matches))

    def calculate_flesch_reading_ease(self, total_words: int, total_sentences: int, total_syllables: int) -> float:
        """Calculates Flesch Reading Ease score."""
        if total_words == 0 or total_sentences == 0:
            return 0.0
        score = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
        return max(0.0, min(100.0, round(score, 1)))

    def analyze(self, text: str, duration_seconds: float = None) -> Dict[str, Any]:
        """
        Runs comprehensive fluency analysis on candidate speech transcript.
        """
        if not text or not text.strip():
            return {
                "word_count": 0,
                "sentence_count": 0,
                "filler_count": 0,
                "filler_percentage": 0.0,
                "filler_breakdown": {},
                "lexical_diversity": 0.0,
                "estimated_wpm": 0.0,
                "tempo_status": "No Speech Detected",
                "flesch_reading_ease": 0.0,
                "fluency_score": 0.0,
                "tips": ["No response recorded yet. Speak into the microphone or type your answer."]
            }

        # Tokenization & clean-up
        lower_text = text.lower()
        words = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', lower_text)
        word_count = len(words)

        # Sentence counting
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        sentence_count = max(1, len(sentences))

        # Detect filler words
        filler_breakdown = {}
        total_filler_occurrences = 0
        temp_text = f" {lower_text} "

        for filler in self.sorted_fillers:
            pattern = rf'\b{re.escape(filler)}\b'
            matches = re.findall(pattern, temp_text)
            if matches:
                count = len(matches)
                filler_breakdown[filler] = count
                total_filler_occurrences += count
                # Replace with placeholder to prevent double counting
                temp_text = re.sub(pattern, " <filler> ", temp_text)

        filler_percentage = round((total_filler_occurrences / max(1, word_count)) * 100, 1)

        # Lexical Diversity: Type-Token Ratio (TTR)
        unique_tokens = set(words)
        ttr = round(len(unique_tokens) / max(1, word_count), 3) if word_count > 0 else 0.0

        # Readability & Syllables
        total_syllables = sum(self.count_syllables(w) for w in words)
        flesch_score = self.calculate_flesch_reading_ease(word_count, sentence_count, total_syllables)

        # Words Per Minute (WPM)
        if duration_seconds and duration_seconds > 0:
            wpm = round((word_count / duration_seconds) * 60, 1)
        else:
            # Baseline speaking estimate: ~135 WPM standard interview pace
            wpm = round(min(180.0, max(80.0, word_count / 0.8)), 1) if word_count < 15 else 135.0

        if wpm < config.WPM_SLOW_THRESHOLD:
            tempo_status = "Pacing: Slow / Hesitant"
        elif wpm > config.WPM_FAST_THRESHOLD:
            tempo_status = "Pacing: Fast / Rushed"
        else:
            tempo_status = "Pacing: Optimal & Clear"

        # Fluency Scoring (0 - 100)
        # Deduct for high fillers, reward healthy lexical diversity and good pacing
        base_score = 95.0
        # Deduct up to 35 points for high filler ratio
        filler_penalty = min(35.0, filler_percentage * 3.5)
        # Reward healthy vocabulary (TTR between 0.45 and 0.85)
        diversity_bonus = 5.0 if 0.45 <= ttr <= 0.85 else 0.0
        # Pacing bonus/penalty
        pace_penalty = 10.0 if (wpm < 100 or wpm > 190) else 0.0

        fluency_score = max(20.0, min(100.0, round(base_score - filler_penalty + diversity_bonus - pace_penalty, 1)))

        # Actionable coaching tips
        tips = []
        if total_filler_occurrences > 3:
            top_fillers = sorted(filler_breakdown.items(), key=lambda x: x[1], reverse=True)[:2]
            top_str = ", ".join([f"'{k}' ({v}x)" for k, v in top_fillers])
            tips.append(f"Noticeable filler usage: {top_str}. Replace verbal pauses with comfortable silence.")

        if wpm > config.WPM_FAST_THRESHOLD:
            tips.append(f"Your speaking rate ({wpm} WPM) is fast. Slow down and articulate key technical verbs.")
        elif wpm < config.WPM_SLOW_THRESHOLD and word_count > 10:
            tips.append(f"Your speaking pace ({wpm} WPM) has prolonged hesitations. Practice structuring your thoughts first.")

        if ttr < 0.35 and word_count > 30:
            tips.append("Lexical variety is low. Try incorporating richer domain-specific vocabulary.")

        if not tips:
            tips.append("Excellent pacing, concise articulation, and minimal filler words!")

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "filler_count": total_filler_occurrences,
            "filler_percentage": filler_percentage,
            "filler_breakdown": filler_breakdown,
            "lexical_diversity": ttr,
            "estimated_wpm": wpm,
            "tempo_status": tempo_status,
            "flesch_reading_ease": flesch_score,
            "fluency_score": fluency_score,
            "tips": tips
        }
