"""
Multi-Persona Conversational Agent for AI Interview Coach.
100% Free & Automatic - Zero User API Keys Required.

Features:
1. Genuine AI Answer Validation (detects wrong, creative, or partial answers and reacts accordingly).
2. Live AI Connectivity Ping & Health Diagnostics.
3. AI-Assisted Custom Persona Generator.
4. Support for both Built-in and Custom Personas with persistence.
"""

import os
import re
import json
import time
import random
from typing import Dict, List, Any, Optional
import httpx
import config
from core.persona_manager import get_all_personas

FREE_PUBLIC_LLM_URL = "https://text.pollinations.ai/openai/chat/completions"

class ConversationAgent:
    def __init__(
        self,
        persona_name: str = "Dr. Maya (NLP & Computational Linguistics Expert)",
        preferred_model: str = "openai"
    ):
        self.all_personas = get_all_personas()
        self.persona_name = persona_name
        self.persona = self.all_personas.get(persona_name, list(self.all_personas.values())[0])
        self.preferred_model = preferred_model
        
        # Auto-detect any environment keys silently (never prompt the user)
        self.groq_key = os.environ.get("GROQ_API_KEY", "").strip()
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
        
        self.last_provider_used = "Auto (Free Public LLM)"

    def set_persona(self, persona_name: str):
        self.all_personas = get_all_personas()
        if persona_name in self.all_personas:
            self.persona_name = persona_name
            self.persona = self.all_personas[persona_name]

    def _build_system_prompt(self, current_question: Dict[str, Any]) -> str:
        return f"""You are {self.persona_name}, acting as the {self.persona['role']} conducting an authentic, high-stakes technical/behavioral interview.
Your persona tone: {self.persona.get('tone', 'Analytical, professional, and rigorous')}
Persona description: {self.persona.get('description', '')}
Special focus: {self.persona.get('special_focus', 'Technical depth and trade-offs')}

Current Question Category: {current_question.get('category', 'Technical')}
Question Asked: "{current_question.get('question', '')}"
Target Rubric Concepts: {', '.join(current_question.get('expected_concepts', []))}

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
        nlp_evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validates candidate response and generates conversational interviewer feedback.
        Automatically checks free public cloud LLM first, then environment keys, then smart linguistics.
        """
        # 1. Try Free Public Cloud LLM (Zero keys required)
        try:
            res = self._call_free_public_llm(candidate_answer, current_question, nlp_evaluation)
            if res:
                self.last_provider_used = "Free Public Cloud AI (Pollinations Llama 3 / Mistral)"
                return {**res, "provider_used": self.last_provider_used}
        except Exception:
            pass

        # 2. Try Groq if key in environment
        if self.groq_key:
            try:
                res = self._call_groq(candidate_answer, current_question, nlp_evaluation)
                if res:
                    self.last_provider_used = "Groq Cloud (Llama 3.3 70B)"
                    return {**res, "provider_used": self.last_provider_used}
            except Exception:
                pass

        # 3. Try Gemini if key in environment
        if self.gemini_key:
            try:
                res = self._call_gemini(candidate_answer, current_question, nlp_evaluation)
                if res:
                    self.last_provider_used = "Google Gemini Flash"
                    return {**res, "provider_used": self.last_provider_used}
            except Exception:
                pass

        # 4. Try Local Ollama if available
        try:
            res = self._call_ollama(candidate_answer, current_question, nlp_evaluation)
            if res:
                self.last_provider_used = "Local Ollama"
                return {**res, "provider_used": self.last_provider_used}
        except Exception:
            pass

        # 5. Default Tier: Built-in Smart Computational Linguistics Dialogue & Exemplar Generator
        self.last_provider_used = "Built-in Computational Linguistics Engine (Local)"
        res = self._generate_smart_linguistics_response(candidate_answer, current_question, nlp_evaluation)
        return {**res, "provider_used": self.last_provider_used}

    def _call_free_public_llm(
        self,
        candidate_answer: str,
        current_question: Dict[str, Any],
        nlp_eval: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
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
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()
                parsed = json.loads(raw_text)
                
                ack = parsed.get("acknowledgment", "Good technical perspective.")
                feedback = parsed.get("conversational_feedback", ack)
                
                return {
                    "validation_verdict": parsed.get("validation_verdict", "Strong / Correct"),
                    "acknowledgment": ack,
                    "conversational_feedback": feedback,
                    "follow_up_question": parsed.get("follow_up_question", "How would you handle failure modes in this setup?"),
                    "model_exemplar_answer": parsed.get("model_exemplar_answer", "")
                }
        return None

    def _call_groq(self, candidate_answer: str, current_question: Dict[str, Any], nlp_eval: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
            "max_tokens": 400,
            "temperature": 0.5,
            "response_format": {"type": "json_object"}
        }
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                ack = parsed.get("acknowledgment", "")
                return {
                    "validation_verdict": parsed.get("validation_verdict", "Strong / Correct"),
                    "acknowledgment": ack,
                    "conversational_feedback": parsed.get("conversational_feedback", ack),
                    "follow_up_question": parsed.get("follow_up_question", ""),
                    "model_exemplar_answer": parsed.get("model_exemplar_answer", "")
                }
        return None

    def _call_gemini(self, candidate_answer: str, current_question: Dict[str, Any], nlp_eval: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        prompt = (
            f"{self._build_system_prompt(current_question)}\n\n"
            f"Candidate Answer: {candidate_answer}\n"
            f"NLP Score: {nlp_eval.get('overall_score')}/100"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 400, "temperature": 0.5, "responseMimeType": "application/json"}
        }
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                parsed = json.loads(raw_text)
                ack = parsed.get("acknowledgment", "")
                return {
                    "validation_verdict": parsed.get("validation_verdict", "Strong / Correct"),
                    "acknowledgment": ack,
                    "conversational_feedback": parsed.get("conversational_feedback", ack),
                    "follow_up_question": parsed.get("follow_up_question", ""),
                    "model_exemplar_answer": parsed.get("model_exemplar_answer", "")
                }
        return None

    def _call_ollama(self, candidate_answer: str, current_question: Dict[str, Any], nlp_eval: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = "http://localhost:11434/api/generate"
        prompt = (
            f"{self._build_system_prompt(current_question)}\n\n"
            f"Candidate Answer: {candidate_answer}\n"
            f"Format as JSON with validation_verdict, acknowledgment, conversational_feedback, follow_up_question, model_exemplar_answer:"
        )
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {"num_predict": 300}
        }
        with httpx.Client(timeout=6.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                parsed = json.loads(resp.json().get("response", "{}"))
                ack = parsed.get("acknowledgment", "")
                return {
                    "validation_verdict": parsed.get("validation_verdict", "Strong / Correct"),
                    "acknowledgment": ack,
                    "conversational_feedback": parsed.get("conversational_feedback", ack),
                    "follow_up_question": parsed.get("follow_up_question", ""),
                    "model_exemplar_answer": parsed.get("model_exemplar_answer", "")
                }
        return None

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
        score = nlp_evaluation.get("overall_score", 50.0)
        q_text = current_question.get("question", "")
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
            verdict = "Factually Questionable / Unconventional"
            ack = "Interesting framing, though you missed the foundational concepts expected for this problem."
            feedback = f"While your narrative is articulate, you did not incorporate key principles like {', '.join(expected[:2]) if expected else 'standard industry patterns'}."
            follow_up = "How would you modify your solution to explicitly satisfy high-availability and fault-tolerance constraints?"
        else:
            verdict = "Strong / Correct" if score >= 75 else "Partially Correct"
            if "Dr. Maya" in self.persona_name:
                ack = "That reflects a sound grasp of computational linguistic principles."
            elif "Alex" in self.persona_name:
                ack = "Practical engineering breakdown with a solid focus on systems architecture."
            elif "Sarah" in self.persona_name:
                ack = "Thank you for walking me through that collaborative narrative."
            else:
                ack = f"Solid analysis aligned with our expectations for {self.persona.get('role', 'interviewer')}."
            
            feedback = f"{ack} You articulated key actions, but let's probe deeper into the edge cases."

            if not star_coverage.get("Result", True) and "Behavioral" in cat:
                follow_up = "What was the concrete, quantitative impact or business metric resulting from your actions?"
            elif keywords.get("missing"):
                missing_term = keywords["missing"][0]
                follow_up = f"How would your architecture explicitly account for or optimize around '{missing_term}'?"
            else:
                follow_up = "If this system experienced a 10x spike in concurrent load, where would the primary bottleneck occur?"

        if expected:
            concepts_str = "; ".join(expected[:2])
            exemplar = f"A senior answer would frame: 'We recognized {concepts_str}. By benchmarking bottlenecks and isolating critical paths, we delivered an optimal, resilient architecture with measurable SLA gains.'"
        else:
            exemplar = "A gold-standard response clearly structures the context (Situation), personal responsibility (Task), concrete tooling choices (Action), and measurable metric improvements (Result)."

        return {
            "validation_verdict": verdict,
            "acknowledgment": ack,
            "conversational_feedback": feedback,
            "follow_up_question": follow_up,
            "model_exemplar_answer": exemplar
        }

    @staticmethod
    def test_connectivity() -> Dict[str, Any]:
        """
        Sends a live probe to the free public cloud LLM to measure round-trip latency
        and verify live AI connectivity status.
        """
        start = time.time()
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": "openai-fast",
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 5
            }
            with httpx.Client(timeout=4.0) as client:
                resp = client.post(FREE_PUBLIC_LLM_URL, headers=headers, json=payload)
                elapsed_ms = int((time.time() - start) * 1000)
                if resp.status_code == 200:
                    return {
                        "online": True,
                        "provider": "Pollinations Cloud (Llama 3 / Mistral / OpenAI)",
                        "model": "openai-fast (High-Speed LLM)",
                        "latency_ms": elapsed_ms,
                        "status_text": "Live & Connected",
                        "fallback_ready": True
                    }
        except Exception as e:
            pass
            
        return {
            "online": False,
            "provider": "Built-in Computational Linguistics Engine",
            "model": "Local Trained ML + Rule Engine (100% Offline)",
            "latency_ms": 0,
            "status_text": "Offline Fallback Active (Zero Latency)",
            "fallback_ready": True
        }

    @staticmethod
    def ai_generate_persona(concept_prompt: str) -> Dict[str, Any]:
        """
        Uses AI to generate a complete custom interviewer persona from a 1-sentence prompt.
        """
        sys_prompt = """You are a persona design assistant for an AI mock interview coach.
Given a short prompt about an interviewer archetype, return a complete persona profile in JSON format:
{
  "name": "Full Name (e.g. Elena Vance)",
  "role": "Specific Job Title & Company Archetype (e.g. Principal Distributed Systems Architect)",
  "description": "2-sentence biography highlighting their background and high standards.",
  "tone": "2-4 adjectives describing how they speak (e.g. Socratic, intense, uncompromising on edge cases)",
  "avatar": "Single emoji best representing them (e.g. 👩‍💻, 🕵️‍♂️, 🧙‍♂️, 🤖, 💼)",
  "default_domain": "One of: Computational Linguistics & NLP, Software Engineering, Machine Learning & Data Science, Behavioral & HR, System Design, Product & Strategy",
  "special_focus": "Specific technical or behavioral topics they will obsessively test"
}
Ensure strictly valid JSON without markdown code fences.
"""
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": "openai-fast",
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": f"Generate interviewer persona for: '{concept_prompt}'"}
                ],
                "temperature": 0.7,
                "jsonMode": True
            }
            with httpx.Client(timeout=6.0) as client:
                resp = client.post(FREE_PUBLIC_LLM_URL, headers=headers, json=payload)
                if resp.status_code == 200:
                    raw = resp.text.strip()
                    if raw.startswith("```json"): raw = raw[7:]
                    if raw.startswith("```"): raw = raw[3:]
                    if raw.endswith("```"): raw = raw[:-3]
                    return json.loads(raw.strip())
        except Exception:
            pass

        # Offline heuristic generator fallback
        words = concept_prompt.lower()
        if "nlp" in words or "ling" in words:
            domain = "Computational Linguistics & NLP"
            avatar = "👩‍🔬"
            role = "Lead NLP Research Scientist"
        elif "system" in words or "scale" in words or "cloud" in words:
            domain = "System Design"
            avatar = "🏗️"
            role = "Principal Cloud Infrastructure Architect"
        elif "behavioral" in words or "hr" in words or "lead" in words:
            domain = "Behavioral & HR"
            avatar = "👩‍💼"
            role = "Executive Leadership Bar Raiser"
        else:
            domain = "Software Engineering"
            avatar = "👨‍💻"
            role = "Staff Software Architect"

        return {
            "name": f"Interviewer ({concept_prompt.title()[:20]})",
            "role": role,
            "description": f"Expert interviewer specializing in {domain}. Probes deeply on architecture, edge cases, and practical trade-offs.",
            "tone": "Direct, analytical, and inquisitive",
            "avatar": avatar,
            "default_domain": domain,
            "special_focus": concept_prompt
        }
