"""
Fluency and Computational Linguistic Metrics Detector.
Analyzes filler words, speech tempo (WPM), lexical diversity (Type-Token Ratio, Hapax Legomena),
readability (Flesch Reading Ease, Gunning Fog index), and syntactic complexity.
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
        word = word.lower().strip(".:;?!,'\"-")
        if not word:
            return 0
        if len(word) <= 3:
            return 1
        word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
        word = re.sub(r'^y', '', word)
        matches = re.findall(r'[aeiouy]{1,2}', word)
        return max(1, len(matches))

    def calculate_flesch_reading_ease(self, total_words: int, total_sentences: int, total_syllables: int) -> float:
        """Calculates Flesch Reading Ease score (0 - 100). Higher = easier/clearer."""
        if total_words == 0 or total_sentences == 0:
            return 0.0
        score = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
        return max(0.0, min(100.0, round(score, 1)))

    def calculate_gunning_fog(self, total_words: int, total_sentences: int, complex_words: int) -> float:
        """Calculates Gunning Fog index (indicates grade level required to understand)."""
        if total_words == 0 or total_sentences == 0:
            return 0.0
        fog = 0.4 * ((total_words / total_sentences) + 100.0 * (complex_words / total_words))
        return round(max(0.0, min(24.0, fog)), 1)

    def analyze(self, text: str, duration_seconds: float = None) -> Dict[str, Any]:
        """
        Runs comprehensive computational linguistics fluency analysis on candidate speech transcript.
        """
        if not text or not text.strip():
            return {
                "word_count": 0,
                "sentence_count": 0,
                "filler_count": 0,
                "filler_percentage": 0.0,
                "filler_breakdown": {},
                "lexical_diversity": 0.0,
                "hapax_legomena_ratio": 0.0,
                "gunning_fog_index": 0.0,
                "avg_sentence_length": 0.0,
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
        avg_sentence_len = round(word_count / sentence_count, 1)

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

        # Lexical Richness: Type-Token Ratio (TTR) & Hapax Legomena
        word_freq = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1

        unique_tokens = len(word_freq)
        ttr = round(unique_tokens / max(1, word_count), 3) if word_count > 0 else 0.0

        # Hapax legomena: words occurring exactly once
        hapax_count = sum(1 for w, c in word_freq.items() if c == 1)
        hapax_ratio = round(hapax_count / max(1, word_count), 3) if word_count > 0 else 0.0

        # Readability & Syllables
        syllables_list = [self.count_syllables(w) for w in words]
        total_syllables = sum(syllables_list)
        complex_words = sum(1 for s in syllables_list if s >= 3)

        flesch_score = self.calculate_flesch_reading_ease(word_count, sentence_count, total_syllables)
        gunning_fog = self.calculate_gunning_fog(word_count, sentence_count, complex_words)

        # Words Per Minute (WPM)
        if duration_seconds and duration_seconds > 0:
            wpm = round((word_count / duration_seconds) * 60, 1)
        else:
            # Baseline speaking estimate: ~135 WPM standard interview pace
            wpm = round(min(180.0, max(80.0, word_count / 0.8)), 1) if word_count < 15 else 138.0

        if wpm < config.WPM_SLOW_THRESHOLD:
            tempo_status = "Pacing: Slow / Hesitant"
        elif wpm > config.WPM_FAST_THRESHOLD:
            tempo_status = "Pacing: Fast / Rushed"
        else:
            tempo_status = "Pacing: Optimal & Clear"

        # Fluency Scoring (0 - 100)
        base_score = 95.0
        filler_penalty = min(35.0, filler_percentage * 3.5)
        diversity_bonus = 5.0 if 0.45 <= ttr <= 0.85 else 0.0
        pace_penalty = 10.0 if (wpm < 100 or wpm > 190) else 0.0

        fluency_score = max(20.0, min(100.0, round(base_score - filler_penalty + diversity_bonus - pace_penalty, 1)))

        # Actionable coaching tips
        tips = []
        if total_filler_occurrences > 3:
            top_fillers = sorted(filler_breakdown.items(), key=lambda x: x[1], reverse=True)[:2]
            top_str = ", ".join([f"'{k}' ({v}x)" for k, v in top_fillers])
            tips.append(f"Noticeable filler usage: {top_str}. Replace verbal pauses with comfortable silence.")

        if wpm > config.WPM_FAST_THRESHOLD:
            tips.append(f"Your speaking rate ({wpm} WPM) is fast. Slow down to articulate technical verbs with precision.")
        elif wpm < config.WPM_SLOW_THRESHOLD and word_count > 10:
            tips.append(f"Your speaking pace ({wpm} WPM) has prolonged hesitations. Pre-structure your response using STAR.")

        if ttr < 0.35 and word_count > 30:
            tips.append("Lexical variety is low. Incorporate richer domain-specific technical terminology.")

        if gunning_fog > 16:
            tips.append("Sentence structure is overly dense (Fog index > 16). Break multi-clause sentences into direct statements.")

        if not tips:
            tips.append("Outstanding fluency, balanced articulation pace, and minimal verbal filler words!")

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_len,
            "filler_count": total_filler_occurrences,
            "filler_percentage": filler_percentage,
            "filler_breakdown": filler_breakdown,
            "lexical_diversity": ttr,
            "hapax_legomena_ratio": hapax_ratio,
            "gunning_fog_index": gunning_fog,
            "flesch_reading_ease": flesch_score,
            "estimated_wpm": wpm,
            "tempo_status": tempo_status,
            "fluency_score": fluency_score,
            "tips": tips
        }
