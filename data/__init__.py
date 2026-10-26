"""Data package for AI Interview Coach."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

def load_question_bank():
    with open(DATA_DIR / "question_bank.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_rubrics():
    with open(DATA_DIR / "rubrics.json", "r", encoding="utf-8") as f:
        return json.load(f)
