"""
FastAPI Server for AI Interview Coach.
High-performance REST API and static frontend server.
Optional configured LLM providers with a clearly identified offline fallback.
"""

import os
import io
import json
import random
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
from data import load_question_bank, load_rubrics
from core.nlp_analyzer import NLPAnalyzer
from core.conversation_agent import ConversationAgent
from core.voice_engine import VoiceEngine
from core.resume_parser import ResumeParser
from core.report_generator import ReportGenerator
from core.session_store import SessionStore
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
    allow_origins=[
        origin.strip() for origin in os.environ.get(
            "CORS_ALLOWED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000"
        ).split(",") if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core singletons
nlp_analyzer = NLPAnalyzer()
voice_engine = VoiceEngine()
resume_parser = ResumeParser()
report_gen = ReportGenerator()
session_store = SessionStore()
question_bank = load_question_bank()
rubrics_data = load_rubrics()


# --- Request/Response Models ---
class EvaluateRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=12000)
    question: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[float] = Field(default=None, gt=0, le=3600)

class ChatRequest(BaseModel):
    persona_name: str = Field(default="Dr. Maya (NLP & Computational Linguistics Expert)", max_length=120)
    candidate_answer: str = Field(min_length=1, max_length=8000)
    current_question: Dict[str, Any]
    nlp_evaluation: Dict[str, Any]
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, max_length=12)
    preferred_model: Optional[str] = Field(default="auto", max_length=100)

class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1200)
    lang: str = Field(default="en", pattern=r"^[a-z]{2}(?:-[A-Z]{2})?$")

class PlaygroundRequest(BaseModel):
    text: str = Field(min_length=1, max_length=12000)

class ReportRequest(BaseModel):
    candidate_name: str = Field(min_length=1, max_length=100)
    persona_name: str = Field(min_length=1, max_length=120)
    session_results: List[Dict[str, Any]] = Field(max_length=100)
    overall_summary: Dict[str, Any]

class SaveSessionRequest(BaseModel):
    candidate_name: str = Field(default="Candidate", max_length=100)
    persona_name: str = Field(min_length=1, max_length=120)
    session_data: Dict[str, Any]

class CreatePersonaRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    role: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=1000)
    tone: str = Field(min_length=1, max_length=200)
    avatar: str = Field(default="🧑‍🏫", max_length=8)
    default_domain: str = Field(default="Software Engineering", max_length=100)
    special_focus: str = Field(default="", max_length=500)

class GeneratePersonaPromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)


# --- API Routes ---

@app.get("/api/health")
def health_check():
    configured_providers = [
        name for name, env_var in (
            ("Groq", "GROQ_API_KEY"),
            ("Google Gemini", "GEMINI_API_KEY"),
            ("OpenAI-compatible", "OPENAI_API_KEY")
        ) if os.environ.get(env_var, "").strip()
    ]
    return {
        "status": "healthy",
        "app": config.APP_TITLE,
        "version": config.APP_VERSION,
        "total_questions": len(question_bank),
        "ai_autofetch_active": True,
        "default_free_model": "GPT-4o-mini via Pollinations.ai",
        "configured_ai_providers": configured_providers,
        "offline_feedback_available": True
    }

@app.get("/api/ai/connectivity")
def check_ai_connectivity():
    """Returns live ping status and latency for active AI connectivity."""
    return ConversationAgent.test_connectivity()

@app.get("/api/llm/models")
def get_available_llm_models():
    """Fetches available free LLM models from Pollinations.ai"""
    import httpx
    models_data = []
    try:
        with httpx.Client(timeout=httpx.Timeout(8.0)) as client:
            resp = client.get("https://text.pollinations.ai/models")
            if resp.status_code == 200:
                raw = resp.json()
                # Pollinations returns a list of model objects or strings
                if isinstance(raw, list):
                    for m in raw:
                        if isinstance(m, dict):
                            models_data.append({
                                "id": m.get("name", m.get("id", "")),
                                "display": m.get("description", m.get("name", "")),
                                "provider": "Pollinations.ai",
                                "free": True
                            })
                        elif isinstance(m, str):
                            models_data.append({"id": m, "display": m, "provider": "Pollinations.ai", "free": True})
    except Exception:
        pass

    # Fallback: known stable models on Pollinations
    if not models_data:
        models_data = [
            {"id": "openai", "display": "GPT-4o-mini (OpenAI via Pollinations)", "provider": "Pollinations.ai", "free": True},
            {"id": "mistral", "display": "Mistral-7B (via Pollinations)", "provider": "Pollinations.ai", "free": True},
            {"id": "llama", "display": "Llama-3 (Meta via Pollinations)", "provider": "Pollinations.ai", "free": True},
            {"id": "claude-haiku", "display": "Claude Haiku (Anthropic via Pollinations)", "provider": "Pollinations.ai", "free": True},
        ]

    # Append env-keyed providers if configured
    if os.environ.get("GROQ_API_KEY", "").strip():
        models_data.append({"id": "groq/llama-3.3-70b-versatile", "display": "Llama-3.3-70B (Groq — env key)", "provider": "Groq", "free": False})
    if os.environ.get("GEMINI_API_KEY", "").strip():
        models_data.append({"id": "gemini/gemini-2.0-flash", "display": "Gemini 2.0 Flash (Google — env key)", "provider": "Google", "free": False})

    return {"models": models_data, "default": "openai", "source": "Pollinations.ai + env providers"}

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
    """Creates a local heuristic persona draft from a prompt."""
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required.")
    generated = ConversationAgent.ai_generate_persona(req.prompt.strip())
    return generated

@app.get("/api/questions")
def get_questions(
    category: Optional[str] = Query(default=None, max_length=100),
    difficulty: Optional[str] = Query(default=None, max_length=20),
    search: Optional[str] = Query(default=None, max_length=200),
    limit: int = Query(default=50, ge=1, le=250),
    random_sample: bool = False,
    sample_size: int = Query(default=3, ge=1, le=20)
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
    agent = ConversationAgent(
        persona_name=req.persona_name,
        preferred_model=req.preferred_model or "auto"
    )
    response_data = agent.generate_response(
        candidate_answer=req.candidate_answer,
        current_question=req.current_question,
        nlp_evaluation=req.nlp_evaluation,
        conversation_history=req.conversation_history
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
        filename = (file.filename or "").lower()
        extension = Path(filename).suffix
        if extension not in {".pdf", ".txt"}:
            raise HTTPException(status_code=415, detail="Only PDF and TXT resumes are supported.")
        content = await file.read(5 * 1024 * 1024 + 1)
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Resume upload exceeds the 5 MB limit.")
        if not content.strip():
            raise HTTPException(status_code=400, detail="The uploaded resume is empty.")
        if extension == ".pdf":
            if not content.startswith(b"%PDF-"):
                raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")
            try:
                raw_text = resume_parser.extract_text_from_pdf(io.BytesIO(content))
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
        else:
            try:
                raw_text = content.decode("utf-8").strip()
            except UnicodeDecodeError as exc:
                raise HTTPException(status_code=400, detail="The TXT resume must use UTF-8 encoding.") from exc
    elif resume_text and resume_text.strip():
        if len(resume_text) > 50000:
            raise HTTPException(status_code=413, detail="Resume text exceeds the 50,000-character limit.")
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
    if job_description and len(job_description) > 12000:
        raise HTTPException(status_code=413, detail="Job description exceeds the 12,000-character limit.")

    parsed = resume_parser.parse_resume(raw_text)
    tailored_questions = resume_parser.generate_tailored_questions(parsed, job_description)
    job_match = (
        resume_parser.match_job_description(parsed, job_description)
        if job_description and job_description.strip() else None
    )

    return {
        "parsed_skills": parsed.get("skills", {}),
        "experience_points": parsed.get("experience_points", []),
        "detected_domains": parsed.get("detected_domains", []),
        "tailored_questions": tailored_questions,
        "job_match": job_match
    }

@app.post("/api/nlp/playground")
def nlp_playground(req: PlaygroundRequest):
    """Quick computational linguistics analysis for the interactive lab."""
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

@app.post("/api/report/pdf")
async def generate_pdf_report(req: ReportRequest):
    """Generates a styled HTML report and converts to PDF bytes for download."""
    html_content = report_gen.generate_html_report(
        candidate_name=req.candidate_name,
        persona_name=req.persona_name,
        session_results=req.session_results,
        overall_summary=req.overall_summary
    )
    # Return HTML for client-side PDF preview/print
    from fastapi.responses import Response
    return Response(content=html_content, media_type="text/html")

@app.get("/api/sessions")
def list_interview_sessions(limit: int = Query(default=20, ge=1, le=100)):
    return session_store.list_sessions(limit)

@app.put("/api/sessions/{session_id}")
def save_interview_session(session_id: str, req: SaveSessionRequest):
    session_results = req.session_data.get("session_results", [])
    if not isinstance(session_results, list) or len(session_results) > 100:
        raise HTTPException(status_code=400, detail="A session may contain at most 100 results.")
    if len(json.dumps(req.session_data, ensure_ascii=False).encode("utf-8")) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Saved interview data exceeds the 2 MB limit.")
    try:
        return session_store.save(
            session_id,
            req.candidate_name.strip() or "Candidate",
            req.persona_name.strip(),
            req.session_data
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/api/sessions/{session_id}")
def get_interview_session(session_id: str):
    try:
        session = session_store.get(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return session

@app.delete("/api/sessions/{session_id}")
def delete_interview_session(session_id: str):
    try:
        deleted = session_store.delete(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return {"deleted": True, "session_id": session_id}

# Mount static directory and fallback
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>AI Interview Coach</h1><p>Static frontend loading...</p>")
