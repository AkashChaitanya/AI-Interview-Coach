"""
AI Interview Coach - Main Streamlit Application
Multimodal Voice & Computational Linguistics Mock Interview Platform
"""

import streamlit as st
import json
import random
from pathlib import Path

# Configure page layout and metadata
st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import config
from data import load_question_bank, load_rubrics
from core.nlp_analyzer import NLPAnalyzer
from core.conversation_agent import ConversationAgent
from core.voice_engine import VoiceEngine
from core.resume_parser import ResumeParser
from ui.styles import get_custom_css
from ui.components import (
    render_header,
    render_persona_card,
    render_evaluation_card
)
from ui.voice_widget import render_voice_recorder_component
from ui.analytics_view import render_session_analytics_dashboard

# Inject custom styling
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize Session State
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.candidate_name = "Candidate"
    st.session_state.selected_persona = list(config.PERSONAS.keys())[0]
    st.session_state.selected_provider = config.AI_PROVIDERS[0]
    st.session_state.active_questions = []
    st.session_state.current_q_index = 0
    st.session_state.session_history = []
    st.session_state.current_answer = ""
    st.session_state.last_evaluation = None
    st.session_state.last_ai_reply = None
    st.session_state.interview_in_progress = False

# Lazy-loaded singletons in st.cache_resource
@st.cache_resource
def get_nlp_analyzer():
    return NLPAnalyzer()

@st.cache_resource
def get_voice_engine():
    return VoiceEngine()

@st.cache_resource
def get_resume_parser():
    return ResumeParser()

@st.cache_data
def get_cached_question_bank():
    return load_question_bank()

@st.cache_data
def get_cached_rubrics():
    return load_rubrics()

nlp_analyzer = get_nlp_analyzer()
voice_engine = get_voice_engine()
resume_parser = get_resume_parser()
all_questions = get_cached_question_bank()
rubrics = get_cached_rubrics()

# -------------------------------------------------------------
# Sidebar Configuration
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Interview Configuration")
    st.session_state.candidate_name = st.text_input(
        "Candidate Name",
        value=st.session_state.candidate_name,
        help="Your name for personalized reports and coaching."
    )

    st.markdown("---")
    st.markdown("### 🧑‍🏫 Interviewer Persona")
    st.session_state.selected_persona = st.selectbox(
        "Select Interviewer",
        options=list(config.PERSONAS.keys()),
        index=0,
        help="Each persona features distinct evaluation focus, conversational style, and domain mastery."
    )

    st.markdown("---")
    st.markdown("### 🤖 AI Engine Provider")
    st.session_state.selected_provider = st.selectbox(
        "Model Provider",
        options=config.AI_PROVIDERS,
        index=0,
        help="Select a provider configured in your environment, or use the clearly labeled offline heuristic."
    )

    st.caption("Configure provider credentials in your local environment; API keys are never requested in this UI.")

    st.markdown("---")
    st.markdown("### 🎯 Question Filtering")
    domains = ["All Domains"] + sorted(list(set(q["category"] for q in all_questions)))
    selected_domain = st.selectbox("Category / Domain", domains, index=0)

    difficulties = ["All Levels", "Junior", "Mid", "Senior"]
    selected_difficulty = st.selectbox("Target Difficulty", difficulties, index=0)

    num_questions = st.slider("Session Length (Questions)", min_value=2, max_value=8, value=3)

    if st.button("🔄 Start New Interview Session", use_container_width=True, type="primary"):
        filtered = all_questions
        if selected_domain != "All Domains":
            filtered = [q for q in filtered if q["category"] == selected_domain]
        if selected_difficulty != "All Levels":
            filtered = [q for q in filtered if q["difficulty"] == selected_difficulty]

        if not filtered:
            filtered = all_questions

        sample_size = min(num_questions, len(filtered))
        st.session_state.active_questions = random.sample(filtered, sample_size)
        st.session_state.current_q_index = 0
        st.session_state.session_history = []
        st.session_state.last_evaluation = None
        st.session_state.last_ai_reply = None
        st.session_state.interview_in_progress = True
        st.success(f"Session started with {sample_size} questions!")
        st.rerun()

    st.markdown("---")
    st.caption("AI Interview Coach v2.0 | Computational Linguistics & AI Project")


# -------------------------------------------------------------
# Main Header
# -------------------------------------------------------------
render_header()

# Create Application Tabs
tab_studio, tab_resume, tab_analytics, tab_bank, tab_architecture = st.tabs([
    "🎙️ Live Interview Studio",
    "📄 Resume Tailored Mode",
    "📊 Linguistic Analytics",
    "📚 Question Bank (220+)",
    "⚙️ NLP Architecture & Models"
])

# -------------------------------------------------------------
# TAB 1: Live Voice Interview Studio
# -------------------------------------------------------------
with tab_studio:
    render_persona_card(st.session_state.selected_persona)

    # Initialize questions if none active
    if not st.session_state.active_questions:
        st.session_state.active_questions = all_questions[:3]
        st.session_state.interview_in_progress = True

    current_idx = st.session_state.current_q_index
    total_qs = len(st.session_state.active_questions)

    if current_idx < total_qs:
        current_q = st.session_state.active_questions[current_idx]

        # Question Presentation Card
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(96, 165, 250, 0.25); border-radius: 14px; padding: 20px; margin: 16px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="tag-badge" style="background: rgba(59, 130, 246, 0.15); color: #60A5FA;">Question {current_idx + 1} of {total_qs}</span>
                <span style="font-size: 0.85rem; color: #94A3B8;">Domain: <strong>{current_q.get('category')}</strong> | Level: <strong>{current_q.get('difficulty')}</strong></span>
            </div>
            <div style="font-size: 1.35rem; font-weight: 700; color: #F8FAFC; margin-top: 6px; line-height: 1.4;">
                "{current_q.get('question')}"
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Interactive Voice Recording & STT Component
        st.components.v1.html(
            render_voice_recorder_component(current_q.get("question", "")),
            height=260
        )

        # Answer Input Form
        st.markdown("#### ✍️ Your Answer Transcript")
        answer_text = st.text_area(
            "Answer Box (Speak using microphone above, or type directly)",
            value="",
            height=130,
            placeholder="Click 'Start Speaking' above to transcribe live voice, or paste/type your interview answer here...",
            key=f"user_answer_input_{current_idx}"
        )

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            submit_pressed = st.button("🚀 Submit Answer & Receive Real-Time Coaching", type="primary", use_container_width=True)
        with c2:
            skip_pressed = st.button("⏭️ Skip Question", use_container_width=True)
        with c3:
            reset_pressed = st.button("🔄 Reset Session", use_container_width=True)

        if reset_pressed:
            st.session_state.current_q_index = 0
            st.session_state.session_history = []
            st.session_state.last_evaluation = None
            st.session_state.last_ai_reply = None
            st.rerun()

        if skip_pressed:
            if st.session_state.current_q_index + 1 < total_qs:
                st.session_state.current_q_index += 1
                st.session_state.last_evaluation = None
                st.session_state.last_ai_reply = None
                st.rerun()
            else:
                st.info("You have reached the end of the session! View the full scorecard in the 'Linguistic Analytics' tab.")

        if submit_pressed:
            if not answer_text.strip():
                st.warning("Please speak into the microphone or type your answer before submitting.")
            else:
                with st.spinner("Analyzing computational linguistics, STAR adherence, and formulating coach response..."):
                    # 1. NLP and STAR Analysis
                    evaluation = nlp_analyzer.analyze_comprehensive(
                        answer=answer_text,
                        question=current_q
                    )

                    # 2. Conversational Follow-up Agent
                    conv_agent = ConversationAgent(
                        persona_name=st.session_state.selected_persona,
                        provider=st.session_state.selected_provider
                    )
                    ai_reply = conv_agent.generate_response(
                        candidate_answer=answer_text,
                        current_question=current_q,
                        nlp_evaluation=evaluation,
                        conversation_history=st.session_state.session_history[-6:]
                    )

                    # Save to state
                    st.session_state.last_evaluation = evaluation
                    st.session_state.last_ai_reply = ai_reply
                    st.session_state.session_history.append({
                        "question": current_q,
                        "answer": answer_text,
                        "evaluation": evaluation,
                        "ai_reply": ai_reply
                    })

        # Display Evaluation if Available
        if st.session_state.last_evaluation and st.session_state.session_history:
            render_evaluation_card(st.session_state.last_evaluation, st.session_state.last_ai_reply)

            # Next Question button
            if current_idx + 1 < total_qs:
                if st.button("➡️ Proceed to Next Question", type="primary"):
                    st.session_state.current_q_index += 1
                    st.session_state.last_evaluation = None
                    st.session_state.last_ai_reply = None
                    st.rerun()
            else:
                st.success("🎉 You have completed all questions in this session!")
                st.info("Check out the 'Linguistic Analytics' tab for your 5-axis competency radar and to download your official assessment report!")

    else:
        st.success("🎉 Session Complete! All questions have been evaluated.")
        if st.button("🔄 Start Another Session"):
            st.session_state.current_q_index = 0
            st.session_state.session_history = []
            st.session_state.last_evaluation = None
            st.session_state.last_ai_reply = None
            st.rerun()


# -------------------------------------------------------------
# TAB 2: Resume & Job Description Tailored Mode
# -------------------------------------------------------------
with tab_resume:
    st.markdown("### 📄 Resume & Job Description Tailored Interview")
    st.markdown("Upload your resume or load a sample to generate **personalized deep-dive interview questions** matching your exact background.")

    col_r1, col_r2 = st.columns([1, 1])

    with col_r1:
        st.markdown("#### 1. Upload or Select Resume")
        uploaded_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])

        sample_choice = st.selectbox(
            "Or load a pre-built sample resume:",
            ["None", "Priya Sharma (Computational Linguist & NLP)", "Alex Chen (Software Engineer)"]
        )

        resume_text = ""
        if uploaded_file is not None:
            if uploaded_file.size > 5 * 1024 * 1024:
                st.error("Resume upload exceeds the 5 MB limit.")
            else:
                try:
                    if uploaded_file.name.lower().endswith(".pdf"):
                        resume_text = resume_parser.extract_text_from_pdf(uploaded_file)
                    else:
                        resume_text = uploaded_file.read().decode("utf-8")
                except (ValueError, UnicodeDecodeError) as exc:
                    st.error(str(exc))
        elif sample_choice == "Priya Sharma (Computational Linguist & NLP)":
            sample_path = config.DATA_DIR / "sample_resumes" / "nlp_computational_linguist.txt"
            if sample_path.exists():
                with open(sample_path, "r", encoding="utf-8") as f:
                    resume_text = f.read()
        elif sample_choice == "Alex Chen (Software Engineer)":
            sample_path = config.DATA_DIR / "sample_resumes" / "software_engineer.txt"
            if sample_path.exists():
                with open(sample_path, "r", encoding="utf-8") as f:
                    resume_text = f.read()

        resume_input = st.text_area("Resume Content Preview", value=resume_text, height=220)

    with col_r2:
        st.markdown("#### 2. Target Job Description (Optional)")
        jd_input = st.text_area(
            "Paste Job Description or Key Requirements",
            height=265,
            placeholder="e.g. Seeking a Senior NLP Engineer proficient in Hugging Face, LLM fine-tuning (LoRA), and high-throughput vector search architectures..."
        )

    if st.button("⚡ Parse Resume & Generate Tailored Questions", type="primary", use_container_width=True):
        if not resume_input.strip():
            st.warning("Please upload a resume or select a sample resume above.")
        else:
            with st.spinner("Parsing resume skills, extracting project bullet points, and synthesizing custom interview questions..."):
                parsed_data = resume_parser.parse_resume(resume_input)
                tailored_qs = resume_parser.generate_tailored_questions(parsed_data, jd_input)

                st.session_state.parsed_resume = parsed_data
                st.session_state.tailored_questions = tailored_qs
                st.success(f"Extracted {sum(len(v) for v in parsed_data.get('skills', {}).values())} skills across {len(parsed_data.get('detected_domains', []))} domains!")

    # Display Parsed Data & Questions
    if "tailored_questions" in st.session_state and st.session_state.tailored_questions:
        st.markdown("---")
        st.markdown("#### 🎯 Synthesized Tailored Questions")

        for idx, tq in enumerate(st.session_state.tailored_questions, start=1):
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 14px; margin-bottom: 10px;">
                <span class="tag-badge">{tq.get('category')}</span>
                <span style="font-size: 0.8rem; color: #94A3B8;">Difficulty: {tq.get('difficulty')}</span>
                <div style="font-size: 1.05rem; font-weight: 600; color: #F1F5F9; margin-top: 6px;">
                    {idx}. {tq.get('question')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🚀 Load These Tailored Questions into Live Studio", type="primary"):
            st.session_state.active_questions = st.session_state.tailored_questions
            st.session_state.current_q_index = 0
            st.session_state.session_history = []
            st.session_state.last_evaluation = None
            st.session_state.last_ai_reply = None
            st.success("Loaded tailored questions! Switch to the 'Live Interview Studio' tab to begin.")


# -------------------------------------------------------------
# TAB 3: Linguistic Analytics Dashboard
# -------------------------------------------------------------
with tab_analytics:
    render_session_analytics_dashboard(
        session_history=st.session_state.session_history,
        candidate_name=st.session_state.candidate_name,
        persona_name=st.session_state.selected_persona
    )


# -------------------------------------------------------------
# TAB 4: Question Bank & Rubric Explorer
# -------------------------------------------------------------
with tab_bank:
    st.markdown(f"### 📚 Curated Open-Source Question Bank ({len(all_questions)} Questions)")
    st.markdown("Explore verified questions categorized across computational linguistics, software engineering, machine learning, and behavioral domains.")

    c_f1, c_f2, c_f3 = st.columns([1, 1, 2])
    with c_f1:
        qb_category = st.selectbox("Filter Domain", ["All"] + sorted(list(set(q["category"] for q in all_questions))), key="qb_cat")
    with c_f2:
        qb_level = st.selectbox("Filter Difficulty", ["All", "Junior", "Mid", "Senior"], key="qb_lvl")
    with c_f3:
        search_query = st.text_input("🔍 Search Question or Keyword", placeholder="e.g. transformer, bpe, cache, deadlocks...")

    displayed_qs = all_questions
    if qb_category != "All":
        displayed_qs = [q for q in displayed_qs if q["category"] == qb_category]
    if qb_level != "All":
        displayed_qs = [q for q in displayed_qs if q["difficulty"] == qb_level]
    if search_query.strip():
        sq = search_query.lower()
        displayed_qs = [q for q in displayed_qs if sq in q["question"].lower() or any(sq in kw.lower() for kw in q.get("keywords", []))]

    st.caption(f"Displaying {len(displayed_qs)} matching questions:")

    for q in displayed_qs[:15]:
        with st.expander(f"[{q.get('category')}] {q.get('question')[:85]}... ({q.get('difficulty')})"):
            st.markdown(f"**Full Question:** {q.get('question')}")
            st.markdown(f"**Target Keywords:** `{', '.join(q.get('keywords', []))}`")
            st.markdown("**Expected Core Concepts:**")
            for concept in q.get("expected_concepts", []):
                st.markdown(f"- {concept}")


# -------------------------------------------------------------
# TAB 5: Computational Linguistics Architecture & Models
# -------------------------------------------------------------
with tab_architecture:
    st.markdown("### 🧠 Computational Linguistics Architecture & Open-Source Stack")
    st.markdown(r"""
    This project is designed around **Computational Linguistics** and **Applied NLP**. Cloud AI providers are optional and have independent pricing, quotas, and availability.

    #### 1. Real-Time Multimodal Voice Pipeline
    - **Speech-to-Text (STT):** Implemented via the HTML5 **Web Speech API** (`SpeechRecognition`), providing client-side, zero-latency transcription without requiring server GPU processing.
    - **Text-to-Speech (TTS):** Dual-tier architecture combining browser-native `speechSynthesis` and server-side `gTTS` (Google Text-to-Speech) with Base64 audio encoding.

    #### 2. In-House Trained Machine Learning Models
    - **STAR Sentence Classifier (`models/star_classifier.pkl`):**
      - Trained using **TF-IDF (1-3 n-grams)** + **Balanced Logistic Regression** on authentic behavioral interview dialogue.
      - Classifies statements into **Situation, Task, Action, Result**, and **General**.
    - **Question Category Classifier (`models/question_classifier.pkl`):**
      - Predicts technical domain and difficulty with **88.89% test accuracy**.

    #### 3. Computational Linguistics Metrics
    - **Fluency & Filler Word Analysis:** Scans for vocal pauses (*um, uh, like, actually, basically, you know*) using regex token boundary matching.
    - **Lexical Diversity (Type-Token Ratio - TTR):** Measures vocabulary richness ($\text{TTR} = \frac{|V|}{N}$).
    - **Readability Index:** Computes **Flesch Reading Ease** ($206.835 - 1.015 \left(\frac{\text{words}}{\text{sentences}}\right) - 84.6 \left(\frac{\text{syllables}}{\text{words}}\right)$).
    - **Speech Rate (WPM):** Tracks articulation pace against the optimal human speaking window (120–165 WPM).
    - **Semantic Relevance Matching:** Cosine similarity over TF-IDF term vectors between the candidate's response and benchmark rubric rubrics.

    #### 4. Optional AI Provider Integrations
    - **Offline feedback:** Local deterministic heuristics; explicitly not an LLM and not a factual verifier.
    - **Groq, Google Gemini, and OpenAI-compatible endpoints:** Enabled through backend environment variables.
    - **Local Ollama:** Only attempted when explicitly enabled.
    - Provider quotas, pricing, and latency are provider-controlled and not guaranteed.
    """)
