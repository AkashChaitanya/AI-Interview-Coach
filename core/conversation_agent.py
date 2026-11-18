"""
Multi-persona conversational agent with optional cloud/local LLM providers.

Features:
1. Pollinations.ai as the primary always-on free LLM (no key required).
2. Optional LLM-based answer feedback with validated structured responses.
3. Configured-provider status and explicit offline feedback mode.
4. Local heuristic custom-persona drafts.
5. Support for both Built-in and Custom Personas with persistence.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
import httpx
from core.persona_manager import get_all_personas

logger = logging.getLogger(__name__)

FREE_PUBLIC_LLM_URL = "https://text.pollinations.ai/openai/chat/completions"
FREE_PUBLIC_MODEL = "openai"  # maps to GPT-4o-mini on Pollinations
FREE_PUBLIC_MODEL_DISPLAY = "GPT-4o-mini via Pollinations.ai"

class ConversationAgent:
    def __init__(
        self,
        persona_name: str = "Dr. Maya (NLP & Computational Linguistics Expert)",
        preferred_model: str = "auto",
        provider: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.all_personas = get_all_personas()
        self.persona_name = persona_name
        self.persona = self.all_personas.get(persona_name, list(self.all_personas.values())[0])
        self.preferred_model = (provider or preferred_model or "auto").strip()
        if self.preferred_model.lower().startswith("automatic"):
            self.preferred_model = "auto"
        self.groq_key = os.environ.get("GROQ_API_KEY", "").strip()
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

        selected = self.preferred_model.lower()
        if api_key:
            if "groq" in selected:
                self.groq_key = api_key.strip()
            elif "gemini" in selected:
                self.gemini_key = api_key.strip()
            elif "openai" in selected:
                self.openai_key = api_key.strip()
        self.last_provider_used = "Offline linguistic feedback (not an LLM)"

    def set_persona(self, persona_name: str):
        self.all_personas = get_all_personas()
        if persona_name in self.all_personas:
            self.persona_name = persona_name
            self.persona = self.all_personas[persona_name]

    def _build_system_prompt(
        self,
        current_question: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        history = conversation_history or []
        prior_turns = "\n".join(
            f"Previous question: {turn.get('question', {}).get('question', '')}\n"
            f"Candidate answer: {str(turn.get('answer', ''))[:1500]}"
            for turn in history[-6:]
        )
        return f"""You are {self.persona_name}, acting as the {self.persona['role']} conducting an authentic, high-stakes technical/behavioral interview.
Your persona tone: {self.persona.get('tone', 'Analytical, professional, and rigorous')}
Persona description: {self.persona.get('description', '')}
Special focus: {self.persona.get('special_focus', 'Technical depth and trade-offs')}

Current Question Category: {current_question.get('category', 'Technical')}
Question Asked: "{current_question.get('question', '')}"
Target Rubric Concepts: {', '.join(current_question.get('expected_concepts', []))}
Previous interview context (do not repeat these questions):
{prior_turns or "No prior answers."}

CRITICAL VALIDATION INSTRUCTIONS:
You must critically evaluate the candidate's answer for technical correctness and depth:
1. IF THE CANDIDATE GIVES A FACTUALLY WRONG OR INCORRECT ANSWER:
   - Identify the specific misconception or technical inaccuracy directly.
   - Politely but firmly explain why their explanation fails in practice.
   - Set "validation_verdict" to "Factually Incorrect".
2. IF THE CANDIDATE GIVES A CREATIVE, UNCONVENTIONAL, OR NOVEL ANSWER:
   - Acknowledge their creative angle, evaluate its trade-offs, and probe hidden edge cases.
   - Set "validation_verdict" to "Creative / Unconventional".
3. IF THE CANDIDATE GIVES A VAGUE, FLIPPANT, OR OFF-TOPIC ANSWER:
   - Call it out directly and refocus them on the core technical question.
   - Set "validation_verdict" to "Off-Topic / Vague".
4. IF THE CANDIDATE GIVES A STRONG TECHNICAL ANSWER:
   - Validate their technical accuracy, highlight what they did well, and probe a deeper architectural challenge.
   - Set "validation_verdict" to "Strong / Correct".

Respond in JSON format with exactly these four keys:
{{
  "validation_verdict": "Strong / Correct" | "Partially Correct" | "Factually Incorrect" | "Creative / Unconventional" | "Off-Topic / Vague",
  "acknowledgment": "A 1-2 sentence direct spoken validation highlighting their correctness, error, or creative angle.",
  "conversational_feedback": "A natural 2-3 sentence spoken response addressing the candidate directly ('You stated that... however...'). This will be spoken aloud to the candidate.",
  "follow_up_question": "A sharp, specific follow-up question digging directly into their stated approach or misconception.",
  "model_exemplar_answer": "A concise gold-standard formulation of how a Staff/Principal engineer would answer this question using the STAR method."
}}
Ensure strictly valid JSON without markdown code fences.
"""

    def generate_response(
        self,
        candidate_answer: str,
        current_question: Dict[str, Any],
        nlp_evaluation: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Validates candidate response and generates conversational interviewer feedback.
        Uses configured providers and clearly labels the deterministic offline fallback.
        """
        providers = self._configured_providers()
        failures = []
        for provider_name, call in providers:
            try:
                result = call(candidate_answer, current_question, nlp_evaluation, conversation_history)
                if result:
                    self.last_provider_used = provider_name
                    return {
                        **result,
                        "provider_used": provider_name,
                        "ai_mode": "llm",
                        "provider_errors": failures
                    }
            except (httpx.HTTPError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                error_name = type(exc).__name__
                logger.warning("AI provider %s failed (%s)", provider_name, error_name)
                failures.append({"provider": provider_name, "error": error_name})

        self.last_provider_used = "Offline linguistic feedback (not an LLM)"
        result = self._generate_smart_linguistics_response(
            candidate_answer, current_question, nlp_evaluation
        )
        return {
            **result,
            "provider_used": self.last_provider_used,
            "ai_mode": "offline",
            "provider_errors": failures
        }

    def _configured_providers(self):
        selected = self.preferred_model.lower()
        if "offline" in selected or selected == "none":
            return []

        providers = []

        # If user explicitly selected an env-keyed provider:
        if "groq" in selected and self.groq_key:
            providers.append(("Groq (Llama-3.3-70b)", self._call_groq_configured))
        elif "gemini" in selected and self.gemini_key:
            providers.append(("Google Gemini", self._call_gemini_configured))
        elif "openai" in selected and self.openai_key:
            providers.append(("OpenAI", self._call_openai_compatible))
        elif "ollama" in selected:
            providers.append(("Local Ollama", self._call_ollama_configured))

        # Free Pollinations provider (always enabled and top default)
        target_model = self.preferred_model if self.preferred_model and self.preferred_model not in ("auto", "none") else FREE_PUBLIC_MODEL
        if "/" in target_model:
            target_model = target_model.split("/")[-1]
        providers.append((
            f"Pollinations.ai ({target_model})",
            lambda a, q, e, h: self._call_pollinations(a, q, e, h, model=target_model)
        ))

        # Fallbacks to any configured env-keyed providers
        if self.groq_key and ("groq" not in selected):
            providers.append(("Groq (Llama-3.3-70b)", self._call_groq_configured))
        if self.gemini_key and ("gemini" not in selected):
            providers.append(("Google Gemini", self._call_gemini_configured))
        if self.openai_key and ("openai" not in selected):
            providers.append(("OpenAI", self._call_openai_compatible))
        if os.environ.get("OLLAMA_ENABLED", "").lower() == "true" and ("ollama" not in selected):
            providers.append(("Local Ollama", self._call_ollama_configured))

        return providers

    def _call_pollinations(self, answer, question, evaluation, history, model: Optional[str] = None):
        details = self._chat_payload(answer, question, evaluation, history)
        payload = {
            "model": model or FREE_PUBLIC_MODEL,
            "messages": [
                {"role": "system", "content": details["system"]},
                {"role": "user", "content": details["user"]}
            ],
            "temperature": 0.4,
            "max_tokens": 600,
            "seed": 42
        }
        with httpx.Client(timeout=httpx.Timeout(30.0, connect=8.0)) as client:
            response = client.post(FREE_PUBLIC_LLM_URL, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            # Strip markdown code fences if present
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return self._validate_response(json.loads(content))

    def _chat_payload(
        self, candidate_answer: str, current_question: Dict[str, Any],
        nlp_evaluation: Dict[str, Any], conversation_history: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        return {
            "system": self._build_system_prompt(current_question, conversation_history),
            "user": (
                f"Candidate answer: {candidate_answer[:8000]}\n"
                f"Evaluation evidence: {json.dumps(nlp_evaluation, ensure_ascii=False)[:4000]}"
            )
        }

    def _call_groq_configured(self, answer, question, evaluation, history):
        return self._call_openai_compatible(
            answer, question, evaluation, history,
            url="https://api.groq.com/openai/v1/chat/completions",
            api_key=self.groq_key,
            model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
            provider_supports_json=True
        )

    def _call_openai_compatible(
        self, answer, question, evaluation, history, url=None, api_key=None,
        model=None, provider_supports_json=True
    ):
        base_url = url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        if not base_url.endswith("/chat/completions"):
            base_url += "/chat/completions"
        credentials = api_key or self.openai_key
        details = self._chat_payload(answer, question, evaluation, history)
        payload = {
            "model": model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": details["system"]},
                {"role": "user", "content": details["user"]}
            ],
            "temperature": 0.4,
            "max_tokens": 500
        }
        if provider_supports_json:
            payload["response_format"] = {"type": "json_object"}
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
            response = client.post(
                base_url, headers={"Authorization": f"Bearer {credentials}"},
                json=payload
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return self._validate_response(json.loads(content))

    def _call_gemini_configured(self, answer, question, evaluation, history):
        model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent"
        )
        details = self._chat_payload(answer, question, evaluation, history)
        payload = {
            "systemInstruction": {"parts": [{"text": details["system"]}]},
            "contents": [{"parts": [{"text": details["user"]}]}],
            "generationConfig": {
                "maxOutputTokens": 500,
                "temperature": 0.4,
                "responseMimeType": "application/json"
            }
        }
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
            response = client.post(url, params={"key": self.gemini_key}, json=payload)
            response.raise_for_status()
            content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return self._validate_response(json.loads(content))

    def _call_ollama_configured(self, answer, question, evaluation, history):
        details = self._chat_payload(answer, question, evaluation, history)
        payload = {
            "model": os.environ.get("OLLAMA_MODEL", "llama3"),
            "prompt": f"{details['system']}\n\n{details['user']}",
            "format": "json",
            "stream": False,
            "options": {"num_predict": 500}
        }
        with httpx.Client(timeout=httpx.Timeout(30.0, connect=2.0)) as client:
            response = client.post(f"{self.ollama_host}/api/generate", json=payload)
            response.raise_for_status()
            return self._validate_response(json.loads(response.json()["response"]))

    @staticmethod
    def _validate_response(parsed: Dict[str, Any]) -> Dict[str, Any]:
        verdicts = {
            "Strong / Correct", "Partially Correct", "Factually Incorrect",
            "Creative / Unconventional", "Off-Topic / Vague"
        }
        if not isinstance(parsed, dict) or parsed.get("validation_verdict") not in verdicts:
            raise ValueError("AI response has an invalid verdict")
        required = (
            "acknowledgment", "conversational_feedback",
            "follow_up_question", "model_exemplar_answer"
        )
        if any(not isinstance(parsed.get(key), str) or not parsed[key].strip() for key in required):
            raise ValueError("AI response is missing required text fields")
        return {key: parsed[key].strip()[:3000] for key in ("validation_verdict", *required)}

    def _generate_smart_linguistics_response(
        self,
        candidate_answer: str,
        current_question: Dict[str, Any],
        nlp_evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Rule-based, template-driven, and linguistic feedback dialogue generator.
        Runs 100% offline with zero external network or API keys.
        """
        star_coverage = nlp_evaluation.get("star", {}).get("coverage", {})
        fluency = nlp_evaluation.get("fluency", {})
        keywords = nlp_evaluation.get("keywords", {})
        cat = current_question.get("category", "")
        expected = current_question.get("expected_concepts", [])

        # Detect if answer is very short or off-topic
        words = fluency.get("word_count", 0)
        matched_kw_count = len(keywords.get("matched", []))

        if words < 12:
            verdict = "Off-Topic / Vague"
            ack = "That was unusually brief and did not address the technical requirements of the question."
            feedback = "You gave a very brief statement without elaborating on the core mechanisms or architectural design."
            follow_up = "Could you walk me through the step-by-step engineering choices or tools you would actually employ?"
        elif matched_kw_count == 0 and words > 15:
            verdict = "Partially Correct"
            ack = "Interesting framing, though you missed the foundational concepts expected for this problem."
            feedback = f"While your narrative is articulate, you did not incorporate key principles like {', '.join(expected[:2]) if expected else 'standard industry patterns'}."
            follow_up = "How would you modify your solution to explicitly satisfy high-availability and fault-tolerance constraints?"
        else:
            verdict = "Partially Correct"
            if "Dr. Maya" in self.persona_name:
                ack = "Your response includes ideas related to computational linguistics."
            elif "Alex" in self.persona_name:
                ack = "Your response includes relevant systems-engineering detail."
            elif "Sarah" in self.persona_name:
                ack = "Thank you for walking me through that collaborative narrative."
            else:
                ack = f"Thank you for sharing your perspective for this {self.persona.get('role', 'interviewer')} interview."
            
            feedback = (
                f"{ack} Offline feedback checks structure and rubric markers only; "
                "it cannot verify factual correctness. Let's probe one area in more detail."
            )

            if not star_coverage.get("Result", True) and "Behavioral" in cat:
                follow_up = "What was the concrete, quantitative impact or business metric resulting from your actions?"
            elif keywords.get("missing"):
                missing_term = keywords["missing"][0]
                follow_up = f"How would your architecture explicitly account for or optimize around '{missing_term}'?"
            else:
                follow_up = "If this system experienced a 10x spike in concurrent load, where would the primary bottleneck occur?"

        if expected:
            concepts_str = "; ".join(expected[:2])
            exemplar = (
                "Illustrative structure only—replace details with your own experience: "
                f"explain how {concepts_str} informed your decisions, then describe "
                "a verified outcome and what you learned."
            )
        else:
            exemplar = (
                "Illustrative structure only—not a claim about your experience: explain "
                "the context (Situation), your responsibility (Task), concrete actions "
                "(Action), and a verified outcome (Result)."
            )

        return {
            "validation_verdict": verdict,
            "acknowledgment": ack,
            "conversational_feedback": feedback,
            "follow_up_question": follow_up,
            "model_exemplar_answer": exemplar
        }

    @staticmethod
    def test_connectivity() -> Dict[str, Any]:
        import time
        t0 = time.monotonic()
        try:
            with httpx.Client(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
                resp = client.post(
                    FREE_PUBLIC_LLM_URL,
                    json={
                        "model": FREE_PUBLIC_MODEL,
                        "messages": [{"role": "user", "content": "hi"}],
                        "max_tokens": 5
                    }
                )
                latency_ms = round((time.monotonic() - t0) * 1000, 1)
                if resp.status_code == 200:
                    return {
                        "online": True,
                        "provider": "Pollinations.ai",
                        "model": FREE_PUBLIC_MODEL_DISPLAY,
                        "latency_ms": latency_ms,
                        "status_text": "Connected — Free LLM active",
                        "fallback_ready": True,
                        "ai_mode": "llm"
                    }
        except Exception as e:
            pass
        # Check env-keyed providers
        configured = [
            name for name, key_env in (
                ("Groq", "GROQ_API_KEY"),
                ("Google Gemini", "GEMINI_API_KEY"),
                ("OpenAI-compatible", "OPENAI_API_KEY")
            ) if os.environ.get(key_env, "").strip()
        ]
        if os.environ.get("OLLAMA_ENABLED", "").lower() == "true":
            configured.append("Local Ollama")
        if configured:
            return {
                "online": False,
                "provider": ", ".join(configured),
                "model": "Env-key provider(s) configured",
                "latency_ms": 0,
                "status_text": "Pollinations offline; env providers configured",
                "fallback_ready": True,
                "ai_mode": "configured"
            }
        return {
            "online": False,
            "provider": "None",
            "model": "Offline fallback only",
            "latency_ms": 0,
            "status_text": "No LLM available — using offline linguistics",
            "fallback_ready": True,
            "ai_mode": "offline"
        }

    @staticmethod
    def ai_generate_persona(concept_prompt: str) -> Dict[str, Any]:
        system = """You are a creative AI persona designer. Given a 1-sentence concept, generate a realistic interview persona. 
Respond ONLY with valid JSON (no markdown):
{
  "name": "Full name + credential (e.g. Dr. Priya Nair, PhD)",
  "role": "Specific job title",
  "description": "2-sentence bio about their background and interview style",
  "tone": "Adjective list of their interview style (3-4 words)",
  "avatar": "Single relevant emoji",
  "domain": "One of: Software Engineering | Computational Linguistics & NLP | System Design | Machine Learning & Data Science | Behavioral & HR | Product & Strategy",
  "special_focus": "2-3 specific technical topics they probe on"
}"""
        try:
            with httpx.Client(timeout=httpx.Timeout(20.0, connect=8.0)) as client:
                resp = client.post(
                    FREE_PUBLIC_LLM_URL,
                    json={
                        "model": FREE_PUBLIC_MODEL,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": concept_prompt}
                        ],
                        "max_tokens": 300,
                        "temperature": 0.7,
                        "seed": 99
                    }
                )
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"].strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                data = json.loads(content)
                data["ai_mode"] = "llm"
                data["provider_used"] = "Pollinations.ai (GPT-4o-mini)"
                return data
        except Exception as e:
            # Heuristic fallback
            words = concept_prompt.lower()
            if "nlp" in words or "ling" in words: domain, avatar, role = "Computational Linguistics & NLP", "👩‍🔬", "Lead NLP Research Scientist"
            elif "system" in words or "scale" in words: domain, avatar, role = "System Design", "🏗️", "Principal Cloud Architect"
            elif "behavioral" in words or "hr" in words: domain, avatar, role = "Behavioral & HR", "👩‍💼", "Executive Bar Raiser"
            else: domain, avatar, role = "Software Engineering", "👨‍💻", "Staff Software Architect"
            return {
                "name": f"Interviewer ({concept_prompt.title()[:25]})",
                "role": role, "description": f"Expert interviewer in {domain}.",
                "tone": "Direct, analytical, inquisitive", "avatar": avatar,
                "domain": domain, "special_focus": concept_prompt,
                "ai_mode": "offline", "provider_used": "Local heuristic"
            }
