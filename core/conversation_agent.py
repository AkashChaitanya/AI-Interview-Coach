"""
Multi-Persona Conversational Agent for AI Interview Coach.
Supports:
1. Built-in Offline Intelligent NLP Dialogue Agent (Zero API Key, 100% Free)
2. Groq Cloud API (Free Llama 3.3 70B / Llama 3 8B with sub-200ms latency)
3. Google Gemini Free Tier API (Gemini Flash)
4. Local Ollama (localhost:11434)
"""

import json
import os
import re
import random
from typing import Dict, List, Any, Optional
import httpx
import config

class ConversationAgent:
    def __init__(
        self,
        persona_name: str = "Dr. Maya (NLP & Computational Linguistics Expert)",
        provider: str = "Offline Intelligent NLP Engine (Built-in, 100% Free & Private)",
        api_key: Optional[str] = None
    ):
        self.persona_name = persona_name
        self.persona = config.PERSONAS.get(persona_name, list(config.PERSONAS.values())[0])
        self.provider = provider
        self.api_key = api_key or os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self.history = []

    def set_persona(self, persona_name: str):
        if persona_name in config.PERSONAS:
            self.persona_name = persona_name
            self.persona = config.PERSONAS[persona_name]

    def set_provider(self, provider: str, api_key: Optional[str] = None):
        self.provider = provider
        if api_key:
            self.api_key = api_key

    def _build_system_prompt(self, current_question: Dict[str, Any]) -> str:
        return f"""You are {self.persona_name}, acting as the {self.persona['role']} conducting an authentic professional interview.
Your interview tone is: {self.persona['tone']}
Current question category: {current_question.get('category', 'Technical')}
Current question prompt: {current_question.get('question', '')}
Expected concepts: {', '.join(current_question.get('expected_concepts', []))}

Your role is to:
1. Actively listen to the candidate's response.
2. Provide a 1-sentence constructive acknowledgment highlighting one strong point or a missing aspect.
3. If their answer is incomplete or missing key aspects (like concrete metrics, trade-offs, or STAR result), ask a sharp, targeted follow-up question.
4. Keep your responses concise (2-4 sentences total) so it feels like a real, natural verbal conversation.
Do NOT give away the entire answer immediately. Be conversational, professional, and encouraging.
"""

    def generate_response(
        self,
        candidate_answer: str,
        current_question: Dict[str, Any],
        nlp_evaluation: Dict[str, Any]
    ) -> str:
        """
        Generates conversational interviewer response via selected provider or offline fallback.
        """
        # Check if provider is Groq
        if "Groq" in self.provider and self.api_key:
            try:
                return self._call_groq(candidate_answer, current_question, nlp_evaluation)
            except Exception as e:
                print(f"[Warning] Groq API call failed: {e}. Falling back to built-in offline engine.")

        # Check if provider is Gemini
        if "Gemini" in self.provider and self.api_key:
            try:
                return self._call_gemini(candidate_answer, current_question, nlp_evaluation)
            except Exception as e:
                print(f"[Warning] Gemini API call failed: {e}. Falling back to built-in offline engine.")

        # Check if provider is Ollama
        if "Ollama" in self.provider:
            try:
                return self._call_ollama(candidate_answer, current_question, nlp_evaluation)
            except Exception as e:
                print(f"[Warning] Ollama call failed: {e}. Falling back to built-in offline engine.")

        # Default: Built-in Offline Intelligent NLP Dialogue Agent
        return self._generate_offline_response(candidate_answer, current_question, nlp_evaluation)

    def _call_groq(self, candidate_answer: str, current_question: Dict[str, Any], nlp_eval: Dict[str, Any]) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = [
            {"role": "system", "content": self._build_system_prompt(current_question)},
            {"role": "user", "content": f"Interviewer Question: {current_question.get('question')}\nCandidate Answer: {candidate_answer}\nNLP Score: {nlp_eval.get('overall_score')}/100"}
        ]
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "max_tokens": 200,
            "temperature": 0.6
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                raise RuntimeError(f"Groq error {resp.status_code}: {resp.text}")

    def _call_gemini(self, candidate_answer: str, current_question: Dict[str, Any], nlp_eval: Dict[str, Any]) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        prompt = (
            f"{self._build_system_prompt(current_question)}\n\n"
            f"Question: {current_question.get('question')}\n"
            f"Candidate Answer: {candidate_answer}\n"
            f"Overall Linguistic Score: {nlp_eval.get('overall_score')}/100"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 200, "temperature": 0.6}
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                raise RuntimeError(f"Gemini error {resp.status_code}: {resp.text}")

    def _call_ollama(self, candidate_answer: str, current_question: Dict[str, Any], nlp_eval: Dict[str, Any]) -> str:
        url = "http://localhost:11434/api/generate"
        prompt = (
            f"{self._build_system_prompt(current_question)}\n\n"
            f"Question: {current_question.get('question')}\n"
            f"Candidate Answer: {candidate_answer}\n"
            f"Please respond as the interviewer:"
        )
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 150}
        }
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
            else:
                raise RuntimeError(f"Ollama error {resp.status_code}")

    def _generate_offline_response(
        self,
        candidate_answer: str,
        current_question: Dict[str, Any],
        nlp_evaluation: Dict[str, Any]
    ) -> str:
        """
        Sophisticated rule-based, template-driven, and linguistic feedback dialogue generator.
        Runs 100% offline with zero external network or API keys.
        """
        star_coverage = nlp_evaluation.get("star", {}).get("coverage", {})
        fluency = nlp_evaluation.get("fluency", {})
        keywords = nlp_evaluation.get("keywords", {})
        score = nlp_evaluation.get("overall_score", 50.0)
        q_text = current_question.get("question", "")
        cat = current_question.get("category", "")

        # 1. Acknowledgment openers based on persona
        if "Dr. Maya" in self.persona_name:
            openers = [
                "That's a thoughtful linguistic perspective.",
                "I appreciate your breakdown of the theoretical mechanics.",
                "Good grasp of the foundational principles here.",
                "Interesting technical angle you took on that."
            ]
        elif "Alex" in self.persona_name:
            openers = [
                "Good technical direction.",
                "I like that you immediately thought about the architectural trade-offs.",
                "Practical engineering breakdown.",
                "Fair points on the implementation details."
            ]
        elif "Sarah" in self.persona_name:
            openers = [
                "Thank you for sharing that experience with me.",
                "I really appreciate you giving context to that challenge.",
                "It sounds like that was a high-stakes scenario for your team.",
                "That clearly illustrates your approach to collaboration."
            ]
        else:
            openers = [
                "Thanks for walking me through your thought process.",
                "That gives me a solid overview of your reasoning.",
                "Appreciate that breakdown."
            ]

        opener = random.choice(openers)

        # 2. Targeted follow-up question or feedback
        # Scenario A: Candidate answer was very brief (< 25 words)
        if fluency.get("word_count", 0) < 25:
            follow_up = f"Could you elaborate a bit further on the specific steps you would take or tools you would employ to implement that?"

        # Scenario B: Missing Result in STAR
        elif not star_coverage.get("Result", True) and "Behavioral" in cat:
            follow_up = "You clearly walked through the actions you took. Could you share what the measurable outcome or impact was for the business?"

        # Scenario C: Missing critical domain keywords
        elif keywords.get("missing") and len(keywords.get("missing")) > 0:
            missing_term = keywords["missing"][0]
            if "NLP" in cat:
                follow_up = f"How would your approach account for or integrate concepts like '{missing_term}' in production?"
            elif "Software" in cat or "System" in cat:
                follow_up = f"In terms of scalability and resilience, where does '{missing_term}' factor into your design?"
            else:
                follow_up = f"Could you also speak briefly to how '{missing_term}' played a role in that situation?"

        # Scenario D: High filler words detected
        elif fluency.get("filler_count", 0) >= 3:
            follow_up = "Your core idea is solid. If you were presenting this architecture to an executive committee, how would you summarize the top two trade-offs concisely?"

        # Scenario E: Strong complete answer
        else:
            if "NLP" in cat:
                follow_up = "What would be the biggest failure mode or latency bottleneck of this approach when scaled to 50 languages?"
            elif "Software" in cat:
                follow_up = "If traffic suddenly spiked 10x overnight, which component of your solution would degrade first and how would you mitigate it?"
            elif "System" in cat:
                follow_up = "How would you handle disaster recovery and cross-region replication if the primary data store experienced a partition?"
            else:
                follow_up = "Reflecting on that now, is there anything you would approach differently if you had to do it again?"

        return f"{opener} {follow_up}"
