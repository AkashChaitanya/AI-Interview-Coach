"""
Reusable UI Components for AI Interview Coach.
"""

import streamlit as st
import config
from core.voice_engine import VoiceEngine

voice_engine = VoiceEngine()

def render_header():
    """Renders the top branding hero banner."""
    st.markdown(f"""
    <div class="hero-card">
        <div class="hero-title">🎙️ {config.APP_TITLE}</div>
        <div class="hero-subtitle">{config.APP_SUBTITLE}</div>
        <div>
            <span class="tag-badge">✨ Voice-Enabled STT & TTS</span>
            <span class="tag-badge">⭐ STAR Method Tagger</span>
            <span class="tag-badge">🧠 Computational Linguistics</span>
            <span class="tag-badge">🆓 100% Free & Open-Source</span>
            <span class="tag-badge">⚡ Sub-Second Feedback</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_persona_card(persona_name: str):
    """Renders the interviewer persona profile."""
    p_info = config.PERSONAS.get(persona_name, list(config.PERSONAS.values())[0])
    avatar = p_info.get("avatar", "🧑‍🏫")
    role = p_info.get("role", "Interviewer")
    tone = p_info.get("tone", "Professional")
    desc = p_info.get("description", "")

    st.markdown(f"""
    <div class="interviewer-card">
        <div class="interviewer-avatar">{avatar}</div>
        <div class="interviewer-info">
            <h3>{persona_name.split(' (')[0]} <span style="font-size: 0.85rem; font-weight: normal; color: #60A5FA;">({role})</span></h3>
            <p style="margin-bottom: 4px;">{desc}</p>
            <span style="font-size: 0.78rem; color: #CBD5E1; background: rgba(255,255,255,0.08); padding: 2px 8px; border-radius: 12px;">Tone: {tone}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_evaluation_card(evaluation: dict, ai_response: str):
    """Renders real-time feedback, STAR tags, fluency, and AI follow-up."""
    score = evaluation.get("overall_score", 0.0)
    star = evaluation.get("star", {})
    coverage = star.get("coverage", {})
    fluency = evaluation.get("fluency", {})
    tone = evaluation.get("tone", {})
    keywords = evaluation.get("keywords", {})

    # Overall Score Header
    color = "#4ADE80" if score >= 80 else "#FBBF24" if score >= 60 else "#F87171"
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; padding: 18px; margin: 16px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px; margin-bottom: 14px;">
            <div>
                <span style="font-size: 0.85rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">Answer Performance Score</span>
                <div style="font-size: 2rem; font-weight: 800; color: {color};">{score:.1f} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span></div>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.85rem; color: #94A3B8;">Confidence Tone</span>
                <div style="font-size: 1.1rem; font-weight: 600; color: #F1F5F9;">{tone.get('tone_label', 'Neutral')}</div>
            </div>
        </div>

        <!-- Metric Grid -->
        <div class="metric-grid">
            <div class="metric-tile">
                <div class="metric-label">Words Spoken</div>
                <div class="metric-value">{fluency.get('word_count', 0)}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">Speaking Rate</div>
                <div class="metric-value">{fluency.get('estimated_wpm', 0)} <span style="font-size: 0.8rem; color: #94A3B8;">WPM</span></div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">Filler Words</div>
                <div class="metric-value" style="color: {'#4ADE80' if fluency.get('filler_count', 0) <= 2 else '#F87171'};">{fluency.get('filler_count', 0)}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">STAR Adherence</div>
                <div class="metric-value">{star.get('star_score', 0):.0f}%</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">Keyword Match</div>
                <div class="metric-value">{keywords.get('coverage_pct', 0):.0f}%</div>
            </div>
        </div>

        <!-- STAR Breakdown Pills -->
        <div style="margin: 14px 0;">
            <div style="font-size: 0.82rem; color: #94A3B8; margin-bottom: 6px; text-transform: uppercase;">STAR Method Components Detected:</div>
            <span class="star-pill {'star-present' if coverage.get('Situation') else 'star-missing'}">{'✅' if coverage.get('Situation') else '❌'} Situation</span>
            <span class="star-pill {'star-present' if coverage.get('Task') else 'star-missing'}">{'✅' if coverage.get('Task') else '❌'} Task</span>
            <span class="star-pill {'star-present' if coverage.get('Action') else 'star-missing'}">{'✅' if coverage.get('Action') else '❌'} Action</span>
            <span class="star-pill {'star-present' if coverage.get('Result') else 'star-missing'}">{'✅' if coverage.get('Result') else '❌'} Result</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Interviewer follow-up voice & text
    if ai_response:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.08) 100%); border: 1px solid rgba(96, 165, 250, 0.3); border-radius: 12px; padding: 16px; margin: 12px 0;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="font-size: 1.2rem;">💬</span>
                <strong style="color: #60A5FA;">Interviewer Follow-up & Feedback:</strong>
            </div>
            <p style="color: #F1F5F9; font-size: 1rem; line-height: 1.5; margin: 0 0 10px 0;">"{ai_response}"</p>
        </div>
        """, unsafe_allow_html=True)

        # Audio playback for interviewer's response
        audio_html = voice_engine.get_audio_player_html(ai_response, autoplay=False)
        st.components.v1.html(audio_html, height=50)

    # Coaching Tips
    tips = evaluation.get("coaching_summary", [])
    if tips:
        st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #94A3B8; margin-top: 14px;'>🎯 Actionable Coaching Insights:</div>", unsafe_allow_html=True)
        for tip in tips:
            st.markdown(f"<div class='tip-box'>💡 {tip}</div>", unsafe_allow_html=True)
