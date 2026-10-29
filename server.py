"""
FastAPI Server for AI Interview Coach.
High-performance REST API and static frontend server.
100% Free AI model autofetch - Zero API keys required from user.
"""

import os
import io
import json
import random
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from data import load_question_bank, load_rubrics
from core.nlp_analyzer import NLPAnalyzer
from core.conversation_agent import ConversationAgent
from core.voice_engine import VoiceEngine
from core.resume_parser import ResumeParser
from core.report_generator import ReportGenerator
from core.persona_manager import (
    get_all_personas,
    save_custom_persona,
    delete_custom_persona
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="AI Interview Coach API",
    description="Computational Linguistics & Multimodal Voice Interview Platform",
    version=config.APP_VERSION
)

# Enable CORS for flexible integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core singletons
nlp_analyzer = NLPAnalyzer()
voice_engine = VoiceEngine()
resume_parser = ResumeParser()
report_gen = ReportGenerator()
question_bank = load_question_bank()
rubrics_data = load_rubrics()


# --- Request/Response Models ---
class EvaluateRequest(BaseModel):
    answer: str
    question: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[float] = None

class ChatRequest(BaseModel):
    persona_name: str = "Dr. Maya (NLP & Computational Linguistics Expert)"
    candidate_answer: str
    current_question: Dict[str, Any]
    nlp_evaluation: Dict[str, Any]

class TTSRequest(BaseModel):
    text: str
    lang: str = "en"

class PlaygroundRequest(BaseModel):
    text: str

class ReportRequest(BaseModel):
    candidate_name: str
    persona_name: str
    session_results: List[Dict[str, Any]]
    overall_summary: Dict[str, Any]

class CreatePersonaRequest(BaseModel):
    name: str
    role: str
    description: str
    tone: str
    avatar: str = "🧑‍🏫"
    default_domain: str = "Software Engineering"
    special_focus: str = ""

class GeneratePersonaPromptRequest(BaseModel):
    prompt: str


# --- API Routes ---

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": config.APP_TITLE,
        "version": config.APP_VERSION,
        "total_questions": len(question_bank),
        "ai_autofetch_active": True
    }

@app.get("/api/ai/connectivity")
def check_ai_connectivity():
    """Returns live ping status and latency for active AI connectivity."""
    return ConversationAgent.test_connectivity()

@app.get("/api/personas")
def get_personas():
    """Returns all available built-in and user-created custom personas."""
    return get_all_personas()

@app.post("/api/personas/create")
def create_persona(req: CreatePersonaRequest):
    """Persists a new custom interviewer persona to disk."""
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Persona name is required.")
    data = save_custom_persona(req.name.strip(), req.model_dump())
    return {"success": True, "name": req.name.strip(), "persona": data}

@app.delete("/api/personas/{persona_name}")
def remove_persona(persona_name: str):
    """Deletes a custom interviewer persona. Built-in personas are protected."""
    success = delete_custom_persona(persona_name)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete built-in persona or persona not found.")
    return {"success": True, "deleted": persona_name}

@app.post("/api/personas/ai-generate")
def generate_persona(req: GeneratePersonaPromptRequest):
    """Uses AI to generate a complete custom interviewer persona from a prompt."""
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required.")
    generated = ConversationAgent.ai_generate_persona(req.prompt.strip())
    return generated

@app.get("/api/questions")
def get_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    random_sample: bool = False,
    sample_size: int = 3
):
    filtered = question_bank

    if category and category != "All" and category != "All Domains":
        filtered = [q for q in filtered if q.get("category") == category]

    if difficulty and difficulty != "All" and difficulty != "All Levels":
        filtered = [q for q in filtered if q.get("difficulty") == difficulty]

    if search and search.strip():
        s = search.lower().strip()
        filtered = [
            q for q in filtered
            if s in q.get("question", "").lower()
            or any(s in kw.lower() for kw in q.get("keywords", []))
        ]

    if random_sample and filtered:
        sample_k = min(sample_size, len(filtered))
        return random.sample(filtered, sample_k)

    return filtered[:limit]

@app.get("/api/categories")
def get_categories():
    categories = sorted(list(set(q["category"] for q in question_bank)))
    return ["All Domains"] + categories

@app.post("/api/evaluate")
def evaluate_answer(req: EvaluateRequest):
    """Evaluates candidate response across STAR method, fluency, WPM, and computational linguistics."""
    if not req.answer or not req.answer.strip():
        raise HTTPException(status_code=400, detail="Answer text cannot be empty.")

    evaluation = nlp_analyzer.analyze_comprehensive(
        answer=req.answer,
        question=req.question,
        duration_seconds=req.duration_seconds
    )
    return evaluation

@app.post("/api/chat")
def chat_with_interviewer(req: ChatRequest):
    """
    Validates candidate response and generates conversational interviewer feedback.
    Real AI validation for correct, partially correct, wrong, or creative answers.
    """
    agent = ConversationAgent(persona_name=req.persona_name)
    response_data = agent.generate_response(
        candidate_answer=req.candidate_answer,
        current_question=req.current_question,
        nlp_evaluation=req.nlp_evaluation
    )
    return response_data

@app.post("/api/tts")
def text_to_speech(req: TTSRequest):
    """Converts text to MP3 audio and returns Base64 data URI."""
    audio_uri = voice_engine.text_to_speech_base64(req.text, lang=req.lang)
    if not audio_uri:
        return {"audio_uri": None, "fallback": True}
    return {"audio_uri": audio_uri, "fallback": False}

@app.post("/api/resume/parse")
async def parse_resume(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    sample_name: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None)
):
    """Parses resume (PDF, TXT, or sample) and synthesizes tailored interview questions."""
    raw_text = ""

    if file:
        content = await file.read()
        if file.filename.endswith(".pdf"):
            raw_text = resume_parser.extract_text_from_pdf(io.BytesIO(content))
        else:
            raw_text = content.decode("utf-8", errors="ignore")
    elif resume_text and resume_text.strip():
        raw_text = resume_text.strip()
    elif sample_name:
        if "NLP" in sample_name or "Priya" in sample_name:
            sample_file = BASE_DIR / "data" / "sample_resumes" / "nlp_computational_linguist.txt"
        else:
            sample_file = BASE_DIR / "data" / "sample_resumes" / "software_engineer.txt"
        if sample_file.exists():
            with open(sample_file, "r", encoding="utf-8") as f:
                raw_text = f.read()

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="No resume content provided.")

    parsed = resume_parser.parse_resume(raw_text)
    tailored_questions = resume_parser.generate_tailored_questions(parsed, job_description)

    return {
        "raw_text_preview": raw_text[:400],
        "parsed_skills": parsed.get("skills", {}),
        "experience_points": parsed.get("experience_points", []),
        "detected_domains": parsed.get("detected_domains", []),
        "tailored_questions": tailored_questions
    }

@app.post("/api/nlp/playground")
def nlp_playground(req: PlaygroundRequest):
    """Quick computational linguistics analysis for the interactive lab."""
    if not req.text.strip():
        return {}
    res = nlp_analyzer.analyze_comprehensive(req.text)
    return res

@app.post("/api/report/markdown")
def generate_markdown_report(req: ReportRequest):
    md_content = report_gen.generate_markdown_report(
        candidate_name=req.candidate_name,
        persona_name=req.persona_name,
        session_results=req.session_results,
        overall_summary=req.overall_summary
    )
    return {"markdown": md_content}

@app.post("/api/report/json")
def generate_json_report(req: ReportRequest):
    json_str = report_gen.generate_json_export(
        candidate_name=req.candidate_name,
        persona_name=req.persona_name,
        session_results=req.session_results,
        overall_summary=req.overall_summary
    )
    return json.loads(json_str)

# Mount static directory and fallback
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>AI Interview Coach</h1><p>Static frontend loading...</p>")
