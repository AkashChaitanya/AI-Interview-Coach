"""
Multi-Persona Conversational Agent for AI Interview Coach.
100% Free & Automatic - Zero User API Keys Required.

Architecture:
1. Tier 1: Free Public Cloud LLM Inference (Pollinations OpenAI-compatible endpoint, no keys needed).
2. Tier 2: Auto-detected environment keys (Groq, Gemini, OpenAI) if present in environment or .env.
3. Tier 3: Local Ollama (http://localhost:11434) if active.
4. Tier 4: Built-in Smart Computational Linguistics Dialogue & Exemplar Generator (runs 100% offline).
"""

import os
import re
import json
import random
from typing import Dict, List, Any, Optional
import httpx
import config

FREE_PUBLIC_LLM_URL = "https://text.pollinations.ai/openai/chat/completions"

class ConversationAgent:
    def __init__(
        self,
        persona_name: str = "Dr. Maya (NLP & Computational Linguistics Expert)",
        preferred_model: str = "openai"
    ):
        self.persona_name = persona_name
        self.persona = config.PERSONAS.get(persona_name, list(config.PERSONAS.values())[0])
        self.preferred_model = preferred_model
        
        # Auto-detect any environment keys silently (never prompt the user)
        self.groq_key = os.environ.get("GROQ_API_KEY", "").strip()
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
        
        self.last_provider_used = "Auto (Free Public LLM)"

    def set_persona(self, persona_name: str):
        if persona_name in config.PERSONAS:
            self.persona_name = persona_name
            self.persona = config.PERSONAS[persona_name]

    def _build_system_prompt(self, current_question: Dict[str, Any]) -> str:
        return f"""You are {self.persona_name}, acting as the {self.persona['role']} conducting an authentic, high-caliber professional interview.
Your interview tone is: {self.persona['tone']}
Current question category: {current_question.get('category', 'Technical')}
Current question prompt: "{current_question.get('question', '')}"
Expected concepts: {', '.join(current_question.get('expected_concepts', []))}

Respond in JSON format with exactly the following three keys:
{{
  "acknowledgment": "A 1-2 sentence constructive observation acknowledging a strong point or a missing aspect in the candidate's answer.",
  "follow_up_question": "A sharp, realistic follow-up question digging deeper into their technical architecture, STAR results, trade-offs, or failure modes.",
  "model_exemplar_answer": "A concise (2-3 sentences) gold-standard answer demonstrating how a Staff/Principal engineer would answer this question using the STAR method and precise technical terminology."
}}
Ensure valid JSON only, without markdown code fences.
"""

    def generate_response(
        self,
        candidate_answer: str,
        current_question: Dict[str, Any],
        nlp_evaluation: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generates conversational interviewer response, follow-up, and model exemplar answer.
        Automatically tries free public LLM, then auto-detected keys, then smart linguistics fallback.
        """
        # 1. Try Free Public LLM (Zero keys required)
        try:
            res = self._call_free_public_llm(candidate_answer, current_question, nlp_evaluation)
            if res:
                self.last_provider_used = "Free Public AI (Pollinations Llama/OpenAI)"
                return res
        except Exception as e:
            # Silently fall to next tier
            pass

        # 2. Try Groq if key in environment
        if self.groq_key:
            try:
                res = self._call_groq(candidate_answer, current_question, nlp_evaluation)
                if res:
                    self.last_provider_used = "Groq Cloud (Llama 3.3 70B)"
                    return res
            except Exception:
                pass

        # 3. Try Gemini if key in environment
        if self.gemini_key:
            try:
                res = self._call_gemini(candidate_answer, current_question, nlp_evaluation)
                if res:
                    self.last_provider_used = "Google Gemini Flash"
                    return res
            except Exception:
                pass

        # 4. Try Local Ollama if available
        try:
            res = self._call_ollama(candidate_answer, current_question, nlp_evaluation)
            if res:
                self.last_provider_used = "Local Ollama"
                return res
        except Exception:
            pass

        # 5. Default Tier: Built-in Smart Computational Linguistics Dialogue & Exemplar Generator
        self.last_provider_used = "Built-in Computational Linguistics Engine"
        return self._generate_smart_linguistics_response(candidate_answer, current_question, nlp_evaluation)

    def _call_free_public_llm(
        self,
        candidate_answer: str,
        current_question: Dict[str, Any],
        nlp_eval: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        headers = {"Content-Type": "application/json"}
        messages = [
            {"role": "system", "content": self._build_system_prompt(current_question)},
            {
                "role": "user",
                "content": f"Candidate Answer: \"{candidate_answer}\"\nOverall NLP Score: {nlp_eval.get('overall_score', 0)}/100\nRespond in JSON format."
            }
        ]
        payload = {
            "model": "openai-fast",
            "messages": messages,
            "temperature": 0.5,
            "jsonMode": True
        }
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(FREE_PUBLIC_LLM_URL, headers=headers, json=payload)
            if resp.status_code == 200:
                raw_text = resp.text.strip()
                # Clean any markdown code blocks
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()
                parsed = json.loads(raw_text)
                return {
                    "acknowledgment": parsed.get("acknowledgment", "Good breakdown of your approach."),
                    "follow_up_question": parsed.get("follow_up_question", "How would you handle failure modes in this setup?"),
                    "model_exemplar_answer": parsed.get("model_exemplar_answer", "")
                }
        return None

    def _call_groq(self, candidate_answer: str, current_question: Dict[str, Any], nlp_eval: Dict[str, Any]) -> Optional[Dict[str, str]]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        messages = [
            {"role": "system", "content": self._build_system_prompt(current_question)},
            {"role": "user", "content": f"Candidate Answer: {candidate_answer}\nNLP Score: {nlp_eval.get('overall_score')}/100"}
        ]
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "max_tokens": 350,
            "temperature": 0.5,
            "response_format": {"type": "json_object"}
        }
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return {
                    "acknowledgment": parsed.get("acknowledgment", ""),
                    "follow_up_question": parsed.get("follow_up_question", ""),
                    "model_exemplar_answer": parsed.get("model_exemplar_answer", "")
                }
        return None

    def _call_gemini(self, candidate_answer: str, current_question: Dict[str, Any], nlp_eval: Dict[str, Any]) -> Optional[Dict[str, str]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        prompt = (
            f"{self._build_system_prompt(current_question)}\n\n"
            f"Candidate Answer: {candidate_answer}\n"
            f"NLP Score: {nlp_eval.get('overall_score')}/100"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 350, "temperature": 0.5, "responseMimeType": "application/json"}
        }
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                parsed = json.loads(raw_text)
                return {
                    "acknowledgment": parsed.get("acknowledgment", ""),
                    "follow_up_question": parsed.get("follow_up_question", ""),
                    "model_exemplar_answer": parsed.get("model_exemplar_answer", "")
                }
        return None

    def _call_ollama(self, candidate_answer: str, current_question: Dict[str, Any], nlp_eval: Dict[str, Any]) -> Optional[Dict[str, str]]:
        url = "http://localhost:11434/api/generate"
        prompt = (
            f"{self._build_system_prompt(current_question)}\n\n"
            f"Candidate Answer: {candidate_answer}\n"
            f"Format as JSON with acknowledgment, follow_up_question, model_exemplar_answer:"
        )
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {"num_predict": 250}
        }
        with httpx.Client(timeout=6.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                parsed = json.loads(resp.json().get("response", "{}"))
                return {
                    "acknowledgment": parsed.get("acknowledgment", ""),
                    "follow_up_question": parsed.get("follow_up_question", ""),
                    "model_exemplar_answer": parsed.get("model_exemplar_answer", "")
                }
        return None

    def _generate_smart_linguistics_response(
        self,
        candidate_answer: str,
        current_question: Dict[str, Any],
        nlp_evaluation: Dict[str, Any]
    ) -> Dict[str, str]:
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
        expected = current_question.get("expected_concepts", [])

        # 1. Persona-specific acknowledgments
        if "Dr. Maya" in self.persona_name:
            openers = [
                "That reflects a thoughtful grasp of computational linguistic principles.",
                "I appreciate your breakdown of the theoretical mechanics and representations.",
                "Good technical intuition on the underlying language model behavior."
            ]
        elif "Alex" in self.persona_name:
            openers = [
                "Practical engineering breakdown with a solid focus on systems architecture.",
                "I like that you immediately factored in operational reliability and trade-offs.",
                "Good technical direction on the implementation specifics."
            ]
        elif "Sarah" in self.persona_name:
            openers = [
                "Thank you for sharing that candid narrative—it highlights your collaboration style.",
                "I appreciate how you framed the interpersonal and organizational dynamics.",
                "That clearly illustrates your sense of ownership in high-stakes situations."
            ]
        else:
            openers = [
                "Strong strategic intuition connecting engineering execution to business impact.",
                "Appreciate how you framed the prioritization criteria and metrics."
            ]

        ack = random.choice(openers)

        # 2. Targeted follow-up question
        if fluency.get("word_count", 0) < 25:
            follow_up = "Could you walk me through the specific architectural steps or technologies you would implement in production?"
        elif not star_coverage.get("Result", True) and "Behavioral" in cat:
            follow_up = "You clearly walked through the actions you executed. What was the concrete, measurable outcome or quantitative business impact?"
        elif keywords.get("missing") and len(keywords.get("missing")) > 0:
            missing_term = keywords["missing"][0]
            if "NLP" in cat:
                follow_up = f"How would your architecture explicitly account for or integrate '{missing_term}' when serving high-throughput inference?"
            elif "Software" in cat or "System" in cat:
                follow_up = f"In terms of scalability and fault-tolerance, where does '{missing_term}' factor into your design?"
            else:
                follow_up = f"Could you also speak briefly to how '{missing_term}' played a decisive role in that scenario?"
        elif fluency.get("filler_count", 0) >= 3:
            follow_up = "Your core idea is solid. If you were pitching this architecture to executive leadership in 60 seconds, how would you summarize the top two trade-offs?"
        else:
            if "NLP" in cat:
                follow_up = "What would be the primary latency bottleneck or failure mode of this approach when scaled to 50 low-resource languages?"
            elif "Software" in cat:
                follow_up = "If downstream service requests spiked 10x overnight, which subsystem would degrade first and how would you safeguard it?"
            elif "System" in cat:
                follow_up = "How does this architecture handle cross-region network partitions while preserving data consistency?"
            else:
                follow_up = "Reflecting on that milestone today, what architectural or process decision would you change if rebuilding it from scratch?"

        # 3. Model Exemplar Answer
        if expected:
            concepts_str = "; ".join(expected[:2])
            exemplar = f"A senior answer would frame: 'We identified {concepts_str}. By isolating the critical path and benchmarking latency, we achieved a resilient architecture with quantifiable uptime and SLA gains.'"
        else:
            exemplar = "A gold-standard response frames the technical constraints (Situation), personal responsibility (Task), concrete tooling choices (Action), and measurable metric improvements (Result)."

        return {
            "acknowledgment": ack,
            "follow_up_question": follow_up,
            "model_exemplar_answer": exemplar
        }
