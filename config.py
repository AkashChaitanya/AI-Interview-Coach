"""
Global Configuration for AI Interview Coach.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

APP_TITLE = "AI Interview Coach"
APP_SUBTITLE = "Multimodal Voice & Computational Linguistics Mock Interview Platform"
APP_VERSION = "2.0.0"

# Interview Personas
PERSONAS = {
    "Dr. Maya (NLP & Computational Linguistics Expert)": {
        "role": "Lead NLP Research Scientist",
        "description": "Expert in computational linguistics, syntax, transformers, tokenization, and semantic analysis.",
        "tone": "Academic, rigorous, intellectually curious, encouraging deep linguistic precision.",
        "avatar": "👩‍🔬",
        "default_domain": "Computational Linguistics & NLP"
    },
    "Alex (Rigorous Tech Lead)": {
        "role": "Principal Software Architect",
        "description": "Expert in algorithms, scalable system design, clean architecture, and optimization trade-offs.",
        "tone": "Direct, analytical, focused on production reliability and engineering trade-offs.",
        "avatar": "👨‍💻",
        "default_domain": "Software Engineering"
    },
    "Sarah (Behavioral & HR Director)": {
        "role": "VP of People & Leadership Development",
        "description": "Specialist in the STAR behavioral method, emotional intelligence, leadership, and culture alignment.",
        "tone": "Empathetic, attentive, probing for genuine self-awareness and measurable team impact.",
        "avatar": "👩‍💼",
        "default_domain": "Behavioral & HR"
    },
    "Jordan (Product & Strategy Director)": {
        "role": "Head of Product Innovation",
        "description": "Focuses on user retention, prioritization frameworks (RICE), metric design, and business impact.",
        "tone": "Strategic, user-centric, focused on outcome prioritization and metrics.",
        "avatar": "🧑‍💼",
        "default_domain": "Product & Strategy"
    }
}

# Supported Free AI Providers
AI_PROVIDERS = [
    "Offline Intelligent NLP Engine (Built-in, 100% Free & Private)",
    "Groq Cloud (Llama 3.3 70B - Free, Ultra Low Latency)",
    "Google Gemini (Gemini 1.5/2.0 Flash - Free Tier)",
    "Local Ollama (Llama 3 / Mistral via localhost:11434)"
]

# Speech Rate Benchmarks (Words Per Minute)
WPM_SLOW_THRESHOLD = 115
WPM_OPTIMAL_MIN = 120
WPM_OPTIMAL_MAX = 165
WPM_FAST_THRESHOLD = 180

# Filler Words
FILLER_WORDS = [
    "um", "uh", "er", "ah", "like", "you know", "basically", "actually",
    "literally", "honestly", "sort of", "kind of", "i mean", "right",
    "okay so", "so yeah", "obviously", "to be honest"
]
