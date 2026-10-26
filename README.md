# 🎙️ AI Interview Coach (Voice & Multimodal Conversational Platform)

An intelligent, voice-enabled mock interview platform built for **Computational Linguistics, Applied Natural Language Processing, and Software Engineering**. 

The system acts as an authentic senior technical and behavioral interviewer: it asks questions aloud, transcribes candidate responses in real-time, evaluates linguistic fluency (WPM, filler words, readability), grades adherence to the **STAR framework** (Situation, Task, Action, Result), and conducts dynamic conversational follow-up dialogues.

---

## 🌟 Key Features

- **🎙️ Real-Time Two-Way Voice Agent (100% Free & Open-Source)**:
  - **Speech-to-Text (STT):** Real-time client-side transcription via HTML5 **Web Speech API** with audio waveform visualization and continuous dictation.
  - **Text-to-Speech (TTS):** Browser-native speech synthesis and server-side **gTTS** (Google Text-to-Speech) audio generation with Base64 data streaming.
  - **Hands-Free Studio:** Listen to questions spoken aloud and dictate your answers naturally.

- **💬 Conversational Agent with Adaptive Follow-ups**:
  - Dynamically probes incomplete answers, missing technical nuances, or missing STAR metrics.
  - Multi-persona interviewer profiles:
    - **Dr. Maya:** Lead NLP Research Scientist (Syntax, Semantics, Transformers, Tokenization)
    - **Alex:** Principal Software Architect (System Design, Algorithms, Scalability, Optimization)
    - **Sarah:** VP of People & Leadership (STAR Behavioral, Culture, Conflict Resolution)
    - **Jordan:** Head of Product & Strategy (Prioritization, Metrics, Retention)

- **🧠 Computational Linguistics & NLP Analysis Engine**:
  - **STAR Sentence Classifier:** Pre-trained TF-IDF + Logistic Regression model classifying sentences into *Situation*, *Task*, *Action*, *Result*, or *General*.
  - **Fluency & Filler Word Counter:** Detects verbal pauses (*um, uh, like, actually, basically, you know*).
  - **Speech Tempo Meter:** Evaluates Words-Per-Minute (WPM) against the optimal human speaking window (120–165 WPM).
  - **Lexical Diversity & Readability:** Computes Type-Token Ratio ($\text{TTR} = \frac{|V|}{N}$) and Flesch Reading Ease score.
  - **Domain Keyword Coverage & Cosine Relevance:** Matches candidate responses against benchmark concept rubrics using TF-IDF term vectors.

- **📄 Resume & Job Description Tailored Mode**:
  - Upload PDF or TXT resumes (or use included samples).
  - Automatically parses skills, projects, and target role criteria to generate personalized technical deep-dives and behavioral interview questions.

- **📊 Comprehensive Analytics Dashboard**:
  - 5-Axis Competency Radar Chart (Plotly).
  - Filler word frequency distribution and question-by-question performance tracking.
  - One-click export of official Markdown (`.md`) and JSON assessment reports.

- **🆓 100% Free Stack & Multi-Provider Architecture**:
  - Operates completely offline with **zero external API keys** required via the built-in Intelligent NLP Engine.
  - Seamlessly integrates with free-tier cloud models:
    - **Groq Cloud:** Free Llama 3.3 70B & Llama 3 8B (<200ms latency).
    - **Google Gemini:** Free tier Gemini 1.5/2.0 Flash.
    - **Local Ollama:** Direct integration with locally hosted open-source models (`localhost:11434`).

---

## 🏛️ System Architecture

```text
                                +-----------------------------+
                                |      Web Audio / Mic        |
                                +--------------+--------------+
                                               |
                                               v
+-----------------------+       +-----------------------------+       +-------------------------+
|  Candidate Resume/JD  | ----> |     Streamlit UI Studio     | <---> |   Browser Speech (TTS)  |
+-----------------------+       +--------------+--------------+       +-------------------------+
                                               |
                    +--------------------------+--------------------------+
                    |                                                     |
                    v                                                     v
     +------------------------------+                      +------------------------------+
     |   Computational Linguistics  |                      |    Conversational Agent      |
     |        Analysis Engine       |                      |    (Multi-Persona Brain)     |
     +--------------+---------------+                      +--------------+---------------+
                    |                                                     |
       +------------+------------+                           +------------+------------+
       |                         |                           |                         |
       v                         v                           v                         v
+--------------+          +--------------+            +--------------+          +--------------+
| Fluency &    |          | Trained STAR |            | Built-in     |          | Free APIs    |
| Filler WPM   |          | Classifier   |            | Offline NLP  |          | (Groq/Gemini/|
| Detector     |          | (ML Model)   |            | Rule Agent   |          | Ollama)      |
+--------------+          +--------------+            +--------------+          +--------------+
```

---

## 📂 Project Structure

```text
AI-Interview-Coach/
├── app.py                      # Main Streamlit web application & interface
├── config.py                   # Central configuration & defaults
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment file for free API keys
├── README.md                   # Complete documentation & usage guide
│
├── core/                       # Core engine modules
│   ├── __init__.py
│   ├── voice_engine.py         # Voice TTS, audio streaming, Web Speech bridge
│   ├── conversation_agent.py   # Multi-persona conversational agent with follow-ups
│   ├── nlp_analyzer.py         # Computational linguistics & composite scoring
│   ├── star_evaluator.py       # STAR framework sentence decomposition
│   ├── fluency_detector.py     # Filler word frequency, WPM tempo, readability
│   ├── resume_parser.py        # PDF/TXT resume parser & question generator
│   └── report_generator.py     # Markdown and JSON report exporter
│
├── data/                       # Datasets & evaluation rubrics
│   ├── __init__.py
│   ├── build_datasets.py       # Dataset generator script
│   ├── question_bank.json      # 220+ curated questions across 6 categories
│   ├── rubrics.json            # Model answers, grading criteria, keywords
│   └── sample_resumes/         # Sample resumes for instant demonstration
│       ├── software_engineer.txt
│       └── nlp_computational_linguist.txt
│
├── models/                     # Trained ML models & training pipeline
│   ├── __init__.py
│   ├── train_classifier.py     # Scikit-learn TF-IDF training script
│   ├── star_classifier.pkl     # Serialized STAR sentence classifier
│   └── question_classifier.pkl # Serialized domain classifier (88.9% accuracy)
│
├── ui/                         # Frontend styling & components
│   ├── __init__.py
│   ├── styles.py               # Custom CSS glassmorphism & responsive layout
│   ├── voice_widget.py         # HTML5 Web Speech API voice recording component
│   ├── components.py           # Cards, metric badges, audio players
│   └── analytics_view.py       # Plotly charts, radar charts, scorecard view
│
└── tests/                      # Automated test suite
    ├── __init__.py
    ├── test_nlp.py             # NLP & linguistics tests
    └── test_conversation.py    # Conversation, voice, and resume tests
```

---

## 🚀 Quick Start Guide

### 1. Installation
Clone this repository and install the dependencies:
```bash
git clone https://github.com/AkashChaitanya/AI-Interview-Coach.git
cd AI-Interview-Coach
pip install -r requirements.txt
```

### 2. (Optional) Re-train the NLP Classifiers
The models come pre-trained. If you modify the training dataset in `models/train_classifier.py` or `data/question_bank.json`, re-train with:
```bash
python models/train_classifier.py
```

### 3. Launch the Application
Start the Streamlit application:
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🎙️ How to Use the Voice Interview Studio

1. **Configure Interviewer:** Pick your persona in the sidebar (e.g. *Dr. Maya* for NLP, *Alex* for Software Engineering, *Sarah* for Behavioral).
2. **Listen to Question:** Click the `🔊 Listen to Question` button to hear the question spoken aloud.
3. **Voice Dictation:** Click `🎤 Start Speaking` and dictate your response. Your words will appear live in the transcript box.
4. **Submit & Review:** Click `🚀 Submit Answer & Receive Real-Time Coaching`.
5. **Instant Feedback:** Receive your composite score (0-100), STAR component breakdown (Situation, Task, Action, Result), speech tempo (WPM), filler word count, and listen to the interviewer's voice follow-up!
6. **Analytics & Export:** Head over to the `📊 Linguistic Analytics` tab to inspect your 5-axis competency radar and download your official assessment report.

---

## 🧪 Running Automated Tests
Run the test suite using `pytest`:
```bash
python -m pytest tests/
```

---

## 📄 License & Attribution
Developed as an advanced Computational Linguistics & AI project. Released under the MIT License.
