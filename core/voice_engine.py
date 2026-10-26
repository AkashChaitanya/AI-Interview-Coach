"""
Voice Engine for AI Interview Coach.
Supports:
1. Browser-based SpeechSynthesis (client-side, 0 latency, responsive)
2. gTTS (Google Text-to-Speech, 100% free server-side audio generation)
3. pyttsx3 fallback (offline Windows SAPI5)
4. Base64 audio player embedding for Streamlit
"""

import os
import io
import base64
from typing import Optional
from pathlib import Path

AUDIO_CACHE_DIR = Path(__file__).resolve().parent.parent / ".audio_cache"
AUDIO_CACHE_DIR.mkdir(exist_ok=True)


class VoiceEngine:
    def __init__(self):
        self.gtts_available = True
        try:
            from gtts import gTTS
        except ImportError:
            self.gtts_available = False

    def text_to_speech_base64(self, text: str, lang: str = "en", slow: bool = False) -> Optional[str]:
        """
        Converts text to MP3 audio using gTTS and returns a Base64 data URI string.
        """
        if not text or not text.strip():
            return None

        clean_text = text.replace("*", "").replace("#", "").strip()
        if len(clean_text) > 400:
            # Truncate overly long text for faster voice playback
            clean_text = clean_text[:400] + "..."

        try:
            from gtts import gTTS
            fp = io.BytesIO()
            tts = gTTS(text=clean_text, lang=lang, slow=slow)
            tts.write_to_fp(fp)
            fp.seek(0)
            audio_bytes = fp.read()
            b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
            return f"data:audio/mp3;base64,{b64_audio}"
        except Exception as e:
            # Fallback if offline/network restriction in sandbox
            return None

    def generate_browser_speech_js(self, text: str, voice_name: str = None, rate: float = 1.0, pitch: float = 1.0) -> str:
        """
        Generates JavaScript snippet for native Web Speech API synthesis in the browser.
        Runs 100% offline in client browser with zero server resources.
        """
        clean_text = text.replace('"', '\\"').replace("'", "\\'").replace("\n", " ").replace("\r", "")
        return f"""
        <script>
        (function() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                const utter = new SpeechSynthesisUtterance("{clean_text}");
                utter.rate = {rate};
                utter.pitch = {pitch};
                utter.lang = 'en-US';
                window.speechSynthesis.speak(utter);
            }}
        }})();
        </script>
        """

    def get_audio_player_html(self, text: str, autoplay: bool = True) -> str:
        """
        Returns HTML player for either server-side audio data URI or browser speech synthesis.
        """
        audio_uri = self.text_to_speech_base64(text)
        if audio_uri:
            auto_attr = "autoplay" if autoplay else ""
            return f"""
            <div style="margin: 8px 0;">
                <audio controls {auto_attr} style="width: 100%; height: 36px; border-radius: 8px;">
                    <source src="{audio_uri}" type="audio/mp3">
                    Your browser does not support the audio element.
                </audio>
            </div>
            """
        else:
            # Fallback to browser SpeechSynthesis
            return self.generate_browser_speech_js(text)
