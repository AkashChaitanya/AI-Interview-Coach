# 🎙️ AI Interview Coach (Lovable & Replit Web Edition)

An intelligent, voice-enabled mock interview platform built for **Computational Linguistics, Applied Natural Language Processing, and Software Engineering**. 

Features an authentic, modern website frontend inspired by **Lovable.dev** and **Replit** (Dark Obsidian glassmorphism, animated waveform visualizer, real-time Web Speech STT & TTS, and multi-axis analytics).

---

## 🌟 Key Highlights & Advancements

- **⚡ 100% Free AI Models Autofetched (Zero User API Keys Required)**:
  - Users are **never prompted to enter an API key**.
  - Automatically queries free public high-speed cloud LLMs (OpenAI-compatible inference via Pollinations / Llama 3 / Mistral) with zero rate limits or registration.
  - Automatically detects local Ollama (`localhost:11434`) or environment variables if present.
  - Built-in Smart Computational Linguistics Dialogue & Exemplar Generator acts as an instant offline fallback.

- **🎙️ Real-Time Multimodal Voice Agent**:
  - **Speech-to-Text (STT):** Real-time client-side transcription via HTML5 **Web Speech API** with audio waveform visualization and continuous dictation.
  - **Text-to-Speech (TTS):** Browser-native speech synthesis and server-side **gTTS** (Google Text-to-Speech) audio generation.
  - **Audio Waveform Canvas:** Reacts dynamically to both candidate speech and interviewer audio.

- **🧠 Advanced Computational Linguistics & NLP Engine**:
  - **In-House Trained STAR Classifier (`models/star_classifier.pkl`):** Decomposes responses sentence-by-sentence into **Situation, Task, Action, Result**, and General with interactive color-coded tags.
  - **Syntactic Readability & Complexity:** Computes **Flesch Reading Ease** and **Gunning Fog Index**.
  - **Lexical Diversity & Richness:** Computes **Type-Token Ratio (TTR)** ($\text{TTR} = \frac{|V|}{N}$) and **Hapax Legomena Ratio** (words occurring exactly once).
  - **Fluency & Filler Word Counter:** Scans for vocal pauses (*um, uh, like, actually, basically, you know*).
  - **Speech Tempo Meter:** Evaluates Words-Per-Minute (WPM) against the optimal human speaking window (120–165 WPM).
  - **Confidence & Assertiveness Tone Classifier:** Detects proactive vs. hesitant language markers.

- **💬 Conversational Interviewer Personas**:
  - **Dr. Maya:** Lead NLP Research Scientist (Syntax, Semantics, Transformers, Tokenization)
  - **Alex:** Principal Software Architect (System Design, Algorithms, Scalability, Optimization)
  - **Sarah:** VP of People & Leadership (STAR Behavioral, Culture, Conflict Resolution)
  - **Jordan:** Head of Product & Strategy (Prioritization, Metrics, Retention)

- **📄 Resume & Job Description Tailoring**:
  - Upload PDF or TXT resumes (or load pre-built sample candidates).
  - Extracts competencies across NLP, Languages, Databases, and Cloud.
  - Generates custom deep-dive technical questions and behavioral scenarios with a one-click **Practice in Studio** button.

- **📊 Comprehensive Analytics & Report Export**:
  - 5-Axis Competency Radar Chart (Chart.js).
  - Filler word frequency distribution and question-by-question performance tracking.
  - One-click export of official Markdown (`.md`) and JSON assessment reports.

---

## 🏛️ System Architecture

```text
                                +-----------------------------+
                                |      Web Audio / Mic        |
                                +--------------+--------------+
                                               |
                                               v
+-----------------------+       +-----------------------------+       +-------------------------+
|  Candidate Resume/JD  | ----> |   Lovable/Replit Dark Web   | <---> |   Browser Speech (TTS)  |
+-----------------------+       |   (FastAPI + Tailwind/JS)   |       +-------------------------+
                                +--------------+--------------+
                                               |
                    +--------------------------+--------------------------+
                    |                                                     |
                    v                                                     v
     +------------------------------+                      +------------------------------+
     |   Computational Linguistics  |                      |    Conversational Agent      |
     |        Analysis Engine       |                      |    (Auto-Fetched Free AI)    |
     +--------------+---------------+                      +--------------+---------------+
                    |                                                     |
       +------------+------------+                           +------------+------------+
       |                         |                           |                         |
       v                         v                           v                         v
+--------------+          +--------------+            +--------------+          +--------------+
| Fluency &    |          | Trained STAR |            | Free Public  |          | Built-in     |
| Filler WPM   |          | Classifier   |            | Cloud LLMs   |          | Smart NLP    |
| Detector     |          | (ML Model)   |            | (No API Key) |          | Generator    |
+--------------+          +--------------+            +--------------+          +--------------+
```

---

## 📂 Project Structure

```text
AI-Interview-Coach/
├── main.py                     # Primary runner for the web application
├── server.py                   # High-performance FastAPI backend server
├── config.py                   # Central configuration & defaults
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation & usage guide
│
├── static/                     # Lovable & Replit Inspired Modern Frontend
│   ├── index.html              # Modern single-page web app with Tailwind CSS
│   ├── css/
│   │   └── app.css             # Glassmorphic dark styling, neon glows, waveforms
│   └── js/
│       └── app.js              # Real-time Web Speech STT, audio visualizer, Chart.js
│
├── core/                       # Core engine modules
│   ├── conversation_agent.py   # Multi-persona conversational agent with auto-fetched AI
│   ├── nlp_analyzer.py         # Computational linguistics & composite scoring
│   ├── star_evaluator.py       # STAR framework sentence decomposition
│   ├── fluency_detector.py     # Filler word frequency, WPM tempo, Flesch/Fog readability
│   ├── voice_engine.py         # Voice TTS, audio streaming, Web Speech bridge
│   ├── resume_parser.py        # PDF/TXT resume parser & tailored question generator
│   └── report_generator.py     # Markdown and JSON report exporter
│
├── data/                       # Datasets & evaluation rubrics
│   ├── build_datasets.py       # Dataset generator script
│   ├── question_bank.json      # 221 curated questions across 6 categories
│   ├── rubrics.json            # Model answers, grading criteria, keywords
│   └── sample_resumes/         # Sample resumes for instant demonstration
│       ├── software_engineer.txt
│       └── nlp_computational_linguist.txt
│
├── models/                     # Trained ML models & training pipeline
│   ├── train_classifier.py     # Scikit-learn TF-IDF training script
│   ├── star_classifier.pkl     # Serialized STAR sentence classifier
│   └── question_classifier.pkl # Serialized domain classifier (88.9% accuracy)
│
└── tests/                      # Automated test suite
    ├── test_api.py             # FastAPI endpoints integration tests
    ├── test_conversation.py    # Conversational agent, voice, and resume tests
    └── test_nlp.py             # Fluency, STAR, and NLP analyzer tests
```

---

## 🚀 How to Run the Application

### 1. Launch the Server
Open your terminal in the project directory and run:

```bash
python main.py
```

Or run via Uvicorn:
```bash
uvicorn server:app --reload --port 8000
```

### 2. Open in Browser
Visit **[http://localhost:8000](http://localhost:8000)** in Chrome, Edge, or Safari to experience the real-time voice and conversational studio!

---

## 🧪 Running Automated Tests
Run the complete test suite with `pytest`:
```bash
python -m pytest tests/
```
All 12 tests verify API health, STAR sentence classification, fluency and WPM algorithms, question banks, and conversational auto-fetching.

---

## 📄 License & Attribution
Developed as an advanced Computational Linguistics & AI project. Released under the MIT License.
