"""
Main entry point for AI Interview Coach.
Launches the high-performance FastAPI server with Lovable/Replit-style modern web frontend.
"""

import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("🎙️ AI Interview Coach (Lovable & Replit Web Edition)")
    print("✨ Real-time Voice Agent + Computational Linguistics + STAR ML")
    print("🤖 Optional configured LLM providers with clearly labeled offline fallback")
    print("🌐 Local Server: http://localhost:8000")
    print("=" * 65)
    
    uvicorn.run("server:app", host="127.0.0.1", port=8000, log_level="info")
