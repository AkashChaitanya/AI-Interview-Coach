"""
Persona Manager for AI Interview Coach.
Handles built-in personas and persistent custom interviewer creation & deletion.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import config

CUSTOM_PERSONAS_FILE = config.DATA_DIR / "custom_personas.json"

def _ensure_file():
    if not CUSTOM_PERSONAS_FILE.exists():
        with open(CUSTOM_PERSONAS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)

def get_custom_personas() -> Dict[str, Any]:
    _ensure_file()
    try:
        with open(CUSTOM_PERSONAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def get_all_personas() -> Dict[str, Any]:
    """Returns combined built-in and persistent custom personas."""
    all_p = {}
    # 1. Built-in personas
    for k, v in config.PERSONAS.items():
        all_p[k] = {**v, "built_in": True}
    
    # 2. Custom personas
    custom = get_custom_personas()
    for k, v in custom.items():
        all_p[k] = {**v, "built_in": False}
    
    return all_p

def save_custom_persona(persona_name: str, persona_data: Dict[str, Any]) -> Dict[str, Any]:
    """Saves or updates a custom interviewer persona."""
    _ensure_file()
    custom = get_custom_personas()
    
    clean_data = {
        "role": persona_data.get("role", "Interviewer"),
        "description": persona_data.get("description", "Custom AI Interviewer"),
        "tone": persona_data.get("tone", "Professional, analytical, and inquisitive"),
        "avatar": persona_data.get("avatar", "🧑‍🏫"),
        "default_domain": persona_data.get("default_domain", "Software Engineering"),
        "special_focus": persona_data.get("special_focus", "Deep architectural trade-offs"),
        "built_in": False
    }
    custom[persona_name] = clean_data
    
    with open(CUSTOM_PERSONAS_FILE, "w", encoding="utf-8") as f:
        json.dump(custom, f, indent=2)
        
    return clean_data

def delete_custom_persona(persona_name: str) -> bool:
    """Deletes a custom interviewer persona. Built-in personas cannot be deleted."""
    if persona_name in config.PERSONAS:
        return False
        
    custom = get_custom_personas()
    if persona_name in custom:
        del custom[persona_name]
        with open(CUSTOM_PERSONAS_FILE, "w", encoding="utf-8") as f:
            json.dump(custom, f, indent=2)
        return True
    return False
