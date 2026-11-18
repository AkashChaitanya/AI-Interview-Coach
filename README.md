# 🎙️ AI Interview Coach

An intelligent, voice-enabled mock interview platform built for **Computational Linguistics, Applied Natural Language Processing, and Software Engineering**. 

Features an authentic, modern website frontend inspired by **Lovable.dev** and **Replit** (Dark Obsidian glassmorphism, animated waveform visualizer, real-time Web Speech STT & TTS, and multi-axis analytics).

---

## 🌟 Key Highlights & Advancements

- **🤖 Optional AI providers with an honest offline mode**:
  - Supports Groq, Google Gemini, OpenAI-compatible endpoints, and explicitly enabled local Ollama.
  - Credentials are read from backend environment variables or a local `.env` file and are never sent to browser code.
  - Provider failures are logged without logging credentials or candidate answers; fallback feedback is identified as **not an LLM**.
  - Provider availability, price, quotas, and latency are not guaranteed.

- **🎙️ Real-Time Multimodal Voice Agent**:
  - **Speech-to-Text (STT):** Browser Web Speech API transcription where supported, with editable transcript and typed-response fallback.
  - **Text-to-Speech (TTS):** Browser-native speech synthesis; optional server gTTS requires network access.
  - WPM is reported only when a response duration is supplied; text-only speech timing and pauses are not inferred.

- **🧠 Advanced Computational Linguistics & NLP Engine**:
  - **In-House Trained STAR Classifier (`models/star_classifier.pkl`):** Decomposes responses sentence-by-sentence into **Situation, Task, Action, Result**, and General with interactive color-coded tags.
  - **Syntactic Readability & Complexity:** Computes **Flesch Reading Ease** and **Gunning Fog Index**.
  - **Lexical Diversity & Richness:** Computes **Type-Token Ratio (TTR)** ($\text{TTR} = \frac{|V|}{N}$) and **Hapax Legomena Ratio** (words occurring exactly once).
  - **Fluency & Filler Word Counter:** Scans for vocal pauses (*um, uh, like, actually, basically, you know*).
  - **Timed speech pace:** Evaluates WPM against an adjustable reference window only when response duration is available.
  - **Communication markers:** Counts directness and hedging expressions without inferring psychological confidence or emotion.
  - Optional spaCy-backed lemmas, POS counts, and named entities are included only when the English model is installed.
  - Relevance combines TF-IDF lexical similarity with rubric keyword coverage; it is not an embedding-based semantic score.

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
  - Radar chart uses measured answer relevance, behavioral STAR structure, fluency, clarity, and timed speaking pace; unavailable axes are left blank.
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
     |        Analysis Engine       |                           | (Configured LLM / Offline)  |
     +--------------+---------------+                      +--------------+---------------+
                    |                                                     |
       +------------+------------+                           +------------+------------+
       |                         |                           |                         |
       v                         v                           v                         v
+--------------+          +--------------+            +--------------+          +--------------+
| Fluency &    |          | Trained STAR |            | Configured   |          | Built-in     |
| Filler WPM   |          | Classifier   |            | LLM Provider |          | Offline NLP  |
| Detector     |          | (ML Model)   |            | or Offline   |          | Feedback     |
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
│   ├── conversation_agent.py   # Multi-persona agent with optional configured AI providers
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
Install dependencies and copy the environment template:

```bash
python -m pip install -r requirements.txt
copy .env.example .env
```

Set provider credentials in `.env` only if you want LLM-backed feedback. The app works without them using a labeled offline heuristic. Start the server:

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
The suite covers API behavior, provider/offline labeling, STAR classification, measured versus unavailable speech metrics, question banks, and resume parsing.

## Provider configuration

| Provider | Environment variables |
| --- | --- |
| Groq | `GROQ_API_KEY`, optional `GROQ_MODEL` |
| Google Gemini | `GEMINI_API_KEY`, optional `GEMINI_MODEL` |
| OpenAI-compatible | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` |
| Ollama | `OLLAMA_ENABLED=true`, `OLLAMA_HOST`, `OLLAMA_MODEL` |

Automatic selection tries configured cloud providers before Ollama (only if enabled). Failed calls fall back to offline feedback and are reported in the response. Do not commit `.env`.

## API endpoints

- `GET /api/health`, `GET /api/ai/connectivity`
- `GET /api/personas`, `POST /api/personas/create`, `POST /api/personas/ai-generate`, `DELETE /api/personas/{persona_name}`
- `GET /api/questions`, `GET /api/categories`
- `POST /api/evaluate`, `POST /api/chat`, `POST /api/nlp/playground`
- `POST /api/resume/parse` (PDF/TXT; 5 MB upload limit)
- `POST /api/tts`, `POST /api/report/markdown`, `POST /api/report/json`
- `GET /api/sessions`, `GET /api/sessions/{id}`, `PUT /api/sessions/{id}`, `DELETE /api/sessions/{id}`

## Known limitations

- Offline feedback uses heuristics and does not provide LLM factual validation.
- TF-IDF similarity is lexical rather than embedding-based; skill matching uses a finite built-in taxonomy.
- Browser speech recognition availability and privacy behavior vary by browser; some implementations may transmit audio to the browser vendor.
- Interview history is saved to local SQLite only when the browser's "Save interview history locally" option is enabled. Saved answers may contain personal information; restore or delete them from the studio. Uploaded resumes are not stored.

---

## 📄 License & Attribution
Developed as an advanced Computational Linguistics & AI project. Released under the MIT License.
