/**
 * AI Interview Coach - Frontend Application Engine
 * Lovable & Replit inspired UX/UI, Real-time Voice Agent, and Computational Linguistics.
 */

// --- Global State ---
let state = {
  personas: {},
  currentPersonaKey: "Dr. Maya (NLP & Computational Linguistics Expert)",
  activeQuestions: [],
  currentQIndex: 0,
  sessionHistory: [],
  followUpAsked: new Set(),
  sessionId: null,
  tailoredQuestions: [],
  isRecording: false,
  recognition: null,
  recordingStartTime: null,
  recordingElapsedSeconds: 0,
  transcriptFromSpeech: false,
  finalTranscript: "",
  timerInterval: null,
  currentEvaluation: null,
  currentAiReply: null,
  radarChart: null,
  fillerChart: null,
  audioAnimFrame: null
};

// --- Initialization ---
document.addEventListener("DOMContentLoaded", async () => {
  await loadPersonas();
  await loadQuestionBank();
  initWaveformVisualizer();
  await startNewSession();
  setupDragAndDrop();
  await loadSavedSessions();
  document.getElementById("persistSessionToggle").addEventListener("change", event => {
    const status = document.getElementById("sessionPersistenceStatus");
    status.innerText = event.target.checked
      ? "Future answers will be saved locally after each submission."
      : "Future answers will not be saved; previously saved sessions remain until deleted.";
  });
  // Kick off AI connectivity check and repeat every 60 seconds
  checkAIConnectivity();
  setInterval(checkAIConnectivity, 60000);
  // Close connectivity panel when clicking outside
  document.addEventListener("click", (e) => {
    const panel = document.getElementById("connectivityPanel");
    const badge  = document.getElementById("aiConnectivityBadge");
    if (panel && !panel.classList.contains("hidden") &&
        !panel.contains(e.target) && !badge.contains(e.target)) {
      panel.classList.add("hidden");
    }
  });
});

// --- Tab Switching ---
function switchTab(tabId) {
  const tabs = ["studio", "resume", "analytics", "bank", "lab"];
  tabs.forEach(t => {
    const el = document.getElementById(`workspace-${t}`);
    const btn = document.getElementById(`tab-btn-${t}`);
    if (t === tabId) {
      el.classList.remove("hidden");
      if (btn) {
        btn.classList.add("nav-pill-active", "text-white");
        btn.classList.remove("text-slate-400");
      }
    } else {
      el.classList.add("hidden");
      if (btn) {
        btn.classList.remove("nav-pill-active", "text-white");
        btn.classList.add("text-slate-400");
      }
    }
  });

  if (tabId === "analytics") {
    renderAnalyticsDashboard();
  }
}

// --- Personas API ---
async function loadPersonas() {
  try {
    const res = await fetch("/api/personas");
    state.personas = await res.json();
    const select = document.getElementById("personaSelect");
    select.innerHTML = "";
    Object.keys(state.personas).forEach(key => {
      const opt = document.createElement("option");
      opt.value = key;
      opt.innerText = key;
      select.appendChild(opt);
    });
    updatePersonaDisplay();
    renderCustomPersonasList();
  } catch (e) {
    console.error("Failed to load personas:", e);
  }
}

/**
 * Renders a list of custom personas below the select with 🗑️ delete buttons.
 * Built-in personas are not shown here (they cannot be deleted).
 */
function renderCustomPersonasList() {
  const container = document.getElementById("customPersonasList");
  if (!container) return;
  const customEntries = Object.entries(state.personas).filter(([, p]) => p.built_in === false);
  if (customEntries.length === 0) {
    container.classList.add("hidden");
    container.innerHTML = "";
    return;
  }
  container.classList.remove("hidden");
  container.replaceChildren();
  const heading = document.createElement("div");
  heading.className = "text-[10px] text-slate-500 uppercase font-semibold tracking-wider pt-1 pb-0.5";
  heading.textContent = "Custom Interviewers";
  container.appendChild(heading);
  customEntries.forEach(([key, p]) => {
    const row = document.createElement("div");
    row.className = "flex items-center justify-between gap-2 bg-[#0E131F] rounded-lg px-2.5 py-1.5 border border-white/5";
    const details = document.createElement("div");
    details.className = "flex items-center gap-1.5 min-w-0";
    const avatar = document.createElement("span");
    avatar.className = "text-sm shrink-0";
    avatar.textContent = p.avatar || "🧑‍🏫";
    const name = document.createElement("span");
    name.className = "text-[11px] text-slate-200 font-medium truncate";
    name.textContent = key.split(" (")[0];
    const badge = document.createElement("span");
    badge.className = "text-[10px] text-purple-400 shrink-0";
    badge.textContent = "Custom";
    details.append(avatar, name, badge);
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.title = "Delete this interviewer";
    deleteButton.className = "text-slate-500 hover:text-rose-400 text-xs transition-colors shrink-0";
    deleteButton.textContent = "🗑️";
    deleteButton.addEventListener("click", () => deletePersona(key));
    row.append(details, deleteButton);
    container.appendChild(row);
  });
}

function onPersonaChange() {
  const select = document.getElementById("personaSelect");
  state.currentPersonaKey = select.value;
  updatePersonaDisplay();
}

function updatePersonaDisplay() {
  const p = state.personas[state.currentPersonaKey] || {
    role: "Interviewer",
    tone: "Professional",
    avatar: "🧑‍🏫",
    description: "Senior Technical Interviewer"
  };
  document.getElementById("personaName").innerText = state.currentPersonaKey.split(" (")[0];
  document.getElementById("personaRole").innerText = p.role;
  document.getElementById("personaDesc").innerText = p.description;
  document.getElementById("personaToneBadge").innerText = p.tone;
  document.getElementById("personaAvatar").innerText = p.avatar;
  const replyAvatar = document.getElementById("interviewerReplyAvatar");
  if (replyAvatar) replyAvatar.innerText = p.avatar;
}

// --- Session & Questions ---
async function startNewSession() {
  const domain = document.getElementById("domainFilterSelect").value;
  const difficulty = document.getElementById("difficultyFilterSelect").value;
  const length = parseInt(document.getElementById("sessionLengthSlider").value) || 3;

  try {
    const url = `/api/questions?category=${encodeURIComponent(domain)}&difficulty=${encodeURIComponent(difficulty)}&random_sample=true&sample_size=${length}`;
    const res = await fetch(url);
    const qs = await res.json();
    
    if (qs && qs.length > 0) {
      state.activeQuestions = qs;
      state.currentQIndex = 0;
      state.sessionHistory = [];
      state.followUpAsked = new Set();
      state.sessionId = createSessionId();
      state.recordingElapsedSeconds = 0;
      state.recordingStartTime = null;
      state.transcriptFromSpeech = false;
      state.finalTranscript = "";
      displayCurrentQuestion();
      document.getElementById("evaluationResultsPanel").classList.add("hidden");
      updateSessionScoreHistory();
    }
  } catch (e) {
    console.error("Error starting session:", e);
  }
}

function createSessionId() {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID();
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, character => {
    const value = Math.floor(Math.random() * 16);
    return (character === "x" ? value : (value & 0x3) | 0x8).toString(16);
  });
}

async function saveCurrentSession() {
  const enabled = document.getElementById("persistSessionToggle")?.checked;
  const status = document.getElementById("sessionPersistenceStatus");
  if (!enabled || !state.sessionId || state.sessionHistory.length === 0) return;
  const payload = {
    candidate_name: document.getElementById("candidateNameInput").value.trim() || "Candidate",
    persona_name: state.currentPersonaKey,
    session_data: {
      active_questions: state.activeQuestions,
      current_q_index: state.currentQIndex,
      session_results: state.sessionHistory
    }
  };
  try {
    const response = await fetch(`/api/sessions/${encodeURIComponent(state.sessionId)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || `Save failed (${response.status}).`);
    if (status) status.innerText = `Saved locally · ${result.question_count} response(s).`;
    await loadSavedSessions();
  } catch (error) {
    if (status) status.innerText = `Local save failed: ${error.message || "server unavailable"}.`;
  }
}

async function loadSavedSessions() {
  const select = document.getElementById("savedSessionSelect");
  if (!select) return;
  try {
    const response = await fetch("/api/sessions?limit=30");
    const sessions = await response.json();
    if (!response.ok) throw new Error(`Load failed (${response.status}).`);
    select.replaceChildren();
    if (!sessions.length) {
      const empty = document.createElement("option");
      empty.value = "";
      empty.textContent = "No saved sessions";
      select.appendChild(empty);
      return;
    }
    sessions.forEach(session => {
      const option = document.createElement("option");
      option.value = session.session_id;
      const updated = new Date(session.updated_at).toLocaleString();
      option.textContent = `${session.candidate_name} · ${session.question_count} answers · ${updated}`;
      select.appendChild(option);
    });
  } catch (error) {
    const status = document.getElementById("sessionPersistenceStatus");
    if (status) status.innerText = `Saved-session list unavailable: ${error.message || "server unavailable"}.`;
  }
}

async function restoreSavedSession() {
  const sessionId = document.getElementById("savedSessionSelect").value;
  if (!sessionId) return;
  const status = document.getElementById("sessionPersistenceStatus");
  try {
    const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}`);
    const saved = await response.json();
    if (!response.ok) throw new Error(saved.detail || `Restore failed (${response.status}).`);
    const data = saved.session_data;
    if (!Array.isArray(data.active_questions) || !Array.isArray(data.session_results)) {
      throw new Error("Saved session has an invalid data format.");
    }
    state.sessionId = saved.session_id;
    state.activeQuestions = data.active_questions;
    state.currentQIndex = Math.min(data.current_q_index || 0, state.activeQuestions.length);
    state.sessionHistory = data.session_results;
    state.followUpAsked = new Set(
      data.active_questions.filter(question => question.is_follow_up).map(question => question.id)
    );
    document.getElementById("candidateNameInput").value = saved.candidate_name;
    const personaSelect = document.getElementById("personaSelect");
    if ([...personaSelect.options].some(option => option.value === saved.persona_name)) {
      personaSelect.value = saved.persona_name;
      onPersonaChange();
    }
    displayCurrentQuestion();
    updateSessionScoreHistory();
    const lastTurn = state.sessionHistory[state.sessionHistory.length - 1];
    const currentQuestion = state.activeQuestions[state.currentQIndex];
    if (lastTurn && currentQuestion?.question === lastTurn.question?.question) {
      renderEvaluationResults(lastTurn.evaluation, lastTurn.aiReply || lastTurn.ai_reply);
    }
    if (status) status.innerText = "Interview restored from this device.";
    switchTab("studio");
  } catch (error) {
    if (status) status.innerText = `Restore failed: ${error.message || "server unavailable"}.`;
  }
}

async function deleteSavedSession() {
  const sessionId = document.getElementById("savedSessionSelect").value;
  if (!sessionId || !confirm("Permanently delete this saved interview from this device?")) return;
  const status = document.getElementById("sessionPersistenceStatus");
  try {
    const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}`, { method: "DELETE" });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || `Delete failed (${response.status}).`);
    if (status) status.innerText = "Saved session deleted from this device.";
    await loadSavedSessions();
  } catch (error) {
    if (status) status.innerText = `Delete failed: ${error.message || "server unavailable"}.`;
  }
}

function displayCurrentQuestion() {
  if (state.currentQIndex >= state.activeQuestions.length) {
    onSessionCompleted();
    return;
  }

  const q = state.activeQuestions[state.currentQIndex];
  const total = state.activeQuestions.length;

  document.getElementById("questionCounterBadge").innerText = `Question ${state.currentQIndex + 1} of ${total}`;
  document.getElementById("currentQCategoryBadge").innerText = q.category || "Technical";
  document.getElementById("currentQDifficultyBadge").innerText = q.difficulty || "Mid";
  document.getElementById("currentQuestionText").innerText = `"${q.question}"`;

  // Keywords pills
  const kwContainer = document.getElementById("currentQKeywords");
  kwContainer.innerHTML = "";
  (q.keywords || []).forEach(kw => {
    const chip = document.createElement("span");
    chip.className = "text-[11px] font-mono bg-white/5 text-slate-300 px-2 py-0.5 rounded-md border border-white/10";
    chip.innerText = kw;
    kwContainer.appendChild(chip);
  });

  // Clear previous answer input
  document.getElementById("answerTranscriptInput").value = "";
  document.getElementById("wordCountLive").innerText = "0";
  document.getElementById("wpmEstimateLive").innerText = "--";
  state.recordingElapsedSeconds = 0;
  state.recordingStartTime = null;
  state.transcriptFromSpeech = false;
  state.finalTranscript = "";
  document.getElementById("evaluationResultsPanel").classList.add("hidden");
}

function nextQuestion() {
  const currentQuestion = state.activeQuestions[state.currentQIndex];
  const lastTurn = state.sessionHistory[state.sessionHistory.length - 1];
  const followUp = lastTurn?.aiReply?.follow_up_question?.trim();
  const followUpKey = currentQuestion?.id || currentQuestion?.question;
  if (
    currentQuestion && !currentQuestion.is_follow_up && followUp &&
    lastTurn.question?.question === currentQuestion.question &&
    !state.followUpAsked.has(followUpKey)
  ) {
    state.followUpAsked.add(followUpKey);
    state.activeQuestions.splice(state.currentQIndex + 1, 0, {
      id: `follow_up_${state.currentQIndex + 1}`,
      category: currentQuestion.category,
      difficulty: currentQuestion.difficulty,
      question: followUp,
      keywords: [],
      expected_concepts: [],
      is_follow_up: true
    });
  }
  state.currentQIndex++;
  displayCurrentQuestion();
  saveCurrentSession();
}

function skipQuestion() {
  if (confirm("Skip this question and move to the next?")) {
    nextQuestion();
  }
}

function onSessionCompleted() {
  saveCurrentSession();
  alert("🎉 You have completed all questions in this mock interview session! Switching to your Analytics Dashboard.");
  switchTab("analytics");
}

// --- Live Voice Recording & Web Speech API ---
function initSpeechRecognition() {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) {
    alert("Web Speech API is not supported in this browser. Please use Google Chrome, Microsoft Edge, or Safari for voice dictation.");
    return null;
  }
  const rec = new SpeechRec();
  rec.continuous = true;
  rec.interimResults = true;
  rec.lang = 'en-US';

  rec.onstart = () => {
    state.isRecording = true;
    updateRecordingUI(true);
    state.recordingStartTime = Date.now();
    state.timerInterval = setInterval(updateLiveTimerAndStats, 400);
  };

  rec.onresult = (event) => {
    const finalParts = [];
    const interimParts = [];
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalParts.push(event.results[i][0].transcript.trim());
      } else {
        interimParts.push(event.results[i][0].transcript.trim());
      }
    }
    const txtArea = document.getElementById("answerTranscriptInput");
    if (finalParts.length) {
      state.finalTranscript = [state.finalTranscript, ...finalParts].filter(Boolean).join(" ");
      state.transcriptFromSpeech = true;
    }
    txtArea.value = [state.finalTranscript, ...interimParts].filter(Boolean).join(" ");
    updateLiveTimerAndStats();
  };

  rec.onerror = (e) => {
    console.warn("Speech recognition warning:", e.error);
    if (e.error === "not-allowed" || e.error === "service-not-allowed") {
      alert("Microphone access was denied. Allow microphone access in your browser settings or type your answer instead.");
    } else if (e.error === "audio-capture") {
      alert("No microphone was detected. Connect a microphone or type your answer instead.");
    }
    stopRecording();
  };

  rec.onend = () => {
    stopRecording();
  };

  return rec;
}

function toggleSpeechRecording() {
  if (!state.recognition) {
    state.recognition = initSpeechRecognition();
  }
  if (!state.recognition) return;

  if (state.isRecording) {
    state.recognition.stop();
    stopRecording();
  } else {
    try {
      state.recognition.start();
    } catch (e) {
      console.warn("Recognition start error:", e);
    }
  }
}

function stopRecording() {
  if (state.recordingStartTime !== null) {
    state.recordingElapsedSeconds += Math.max(0, (Date.now() - state.recordingStartTime) / 1000);
    state.recordingStartTime = null;
  }
  state.isRecording = false;
  updateRecordingUI(false);
  if (state.timerInterval) {
    clearInterval(state.timerInterval);
    state.timerInterval = null;
  }
}

function updateRecordingUI(recording) {
  const btn = document.getElementById("toggleRecordBtn");
  const label = document.getElementById("recordBtnLabel");
  const dot = document.getElementById("micStatusDot");
  const text = document.getElementById("micStatusText");
  const timer = document.getElementById("recordingTimer");

  if (recording) {
    btn.className = "flex items-center gap-2 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-lg shadow-rose-600/30 transition-all recording-pulse";
    label.innerText = "Stop Recording";
    dot.className = "w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping";
    text.innerText = "Listening...";
    timer.classList.remove("hidden");
  } else {
    btn.className = "flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-lg shadow-emerald-600/20 transition-all";
    label.innerText = "Start Speaking";
    dot.className = "w-2.5 h-2.5 rounded-full bg-slate-500";
    text.innerText = "Mic Ready";
    timer.classList.add("hidden");
  }
}

function updateLiveTimerAndStats() {
  const text = document.getElementById("answerTranscriptInput").value.trim();
  const words = text ? text.split(/\s+/).length : 0;
  document.getElementById("wordCountLive").innerText = words;

  let seconds = state.recordingElapsedSeconds;
  if (state.recordingStartTime !== null && state.isRecording) {
    seconds += Math.max(0, (Date.now() - state.recordingStartTime) / 1000);
  }
  if (seconds > 0) {
    seconds = Math.floor(seconds);
    const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
    const secs = String(seconds % 60).padStart(2, '0');
    document.getElementById("recordingTimer").innerText = `${mins}:${secs}`;
    const wpm = state.transcriptFromSpeech ? Math.round((words / seconds) * 60) : 0;
    document.getElementById("wpmEstimateLive").innerText = state.transcriptFromSpeech ? wpm : "--";
  } else {
    document.getElementById("wpmEstimateLive").innerText = "--";
  }
}

function clearTranscript() {
  document.getElementById("answerTranscriptInput").value = "";
  document.getElementById("wordCountLive").innerText = "0";
  document.getElementById("wpmEstimateLive").innerText = "--";
  state.recordingElapsedSeconds = 0;
  state.recordingStartTime = null;
  state.transcriptFromSpeech = false;
  state.finalTranscript = "";
}

// --- Text-to-Speech (TTS) Voice Engine ---
function readQuestionAloud() {
  const text = document.getElementById("currentQuestionText").innerText;
  speakText(text);
}

function playInterviewerVoice() {
  const ack = document.getElementById("interviewerAckText").innerText;
  const followUp = document.getElementById("interviewerFollowUpText").innerText;
  speakText(`${ack} ${followUp}`);
}

function speakText(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1.0;
    utter.pitch = 1.0;
    utter.lang = 'en-US';
    window.speechSynthesis.speak(utter);
  } else {
    // Server TTS fallback
    fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    })
    .then(r => r.json())
    .then(data => {
      if (data.audio_uri) {
        const audio = new Audio(data.audio_uri);
        audio.play();
      }
    });
  }
}

// --- Canvas Audio Waveform Visualizer ---
function initWaveformVisualizer() {
  const canvas = document.getElementById("waveformCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let phase = 0;

  function renderWave() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const bars = 48;
    const barWidth = canvas.width / bars;
    
    for (let i = 0; i < bars; i++) {
      let height = 6;
      if (state.isRecording || (window.speechSynthesis && window.speechSynthesis.speaking)) {
        // Active dancing waveform
        height = Math.sin(phase + i * 0.3) * 22 + 28;
      } else {
        // Gentle resting pulse
        height = Math.sin(phase * 0.4 + i * 0.2) * 4 + 8;
      }
      
      const x = i * barWidth;
      const y = (canvas.height - height) / 2;
      
      const grad = ctx.createLinearGradient(0, y, 0, y + height);
      grad.addColorStop(0, '#8B5CF6');
      grad.addColorStop(1, '#06B6D4');
      
      ctx.fillStyle = grad;
      ctx.fillRect(x + 1.5, y, barWidth - 3, height);
    }
    
    phase += 0.08;
    state.audioAnimFrame = requestAnimationFrame(renderWave);
  }
  renderWave();
}

// --- Answer Submission & Computational Evaluation ---
async function submitAnswerForEvaluation() {
  const answer = document.getElementById("answerTranscriptInput").value.trim();
  if (!answer) {
    alert("Please speak into the microphone or type your answer before submitting.");
    return;
  }

  // Stop recording if running
  if (state.isRecording) {
    toggleSpeechRecording();
  }

  const currentQ = state.activeQuestions[state.currentQIndex] || {};
  const btn = document.getElementById("submitAnswerBtn");
  btn.innerHTML = `<span class="animate-spin mr-1">⏳</span> Analyzing Linguistics & AI Follow-up...`;
  btn.disabled = true;

  try {
    // 1. NLP & STAR Evaluation
    const evalRes = await fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        answer: answer,
        question: currentQ,
        duration_seconds: state.transcriptFromSpeech && state.recordingElapsedSeconds > 0
          ? state.recordingElapsedSeconds : null
      })
    });
    if (!evalRes.ok) throw new Error(`Evaluation failed (${evalRes.status}).`);
    const evaluation = await evalRes.json();

    // 2. AI Conversational Follow-up
    const chatRes = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        persona_name: state.currentPersonaKey,
        candidate_answer: answer,
        current_question: currentQ,
        nlp_evaluation: evaluation,
        conversation_history: state.sessionHistory.slice(-6).map(turn => ({
          question: turn.question,
          answer: turn.answer
        }))
      })
    });
    const aiReply = await chatRes.json();
    if (!chatRes.ok) {
      throw new Error(aiReply.detail || `Interviewer response failed (${chatRes.status}).`);
    }

    if (aiReply.ai_mode === "llm" && Number.isFinite(aiReply.answer_score)) {
      evaluation.overall_score = aiReply.answer_score;
      evaluation.score_method = `AI rubric assessment via ${aiReply.provider_used}.`;
      evaluation.ai_score_components = aiReply.score_components;
      evaluation.ai_score_rationale = aiReply.score_rationale;
    }

    // Render Results
    renderEvaluationResults(evaluation, aiReply);

    // Save into history
    state.sessionHistory.push({
      question: currentQ,
      answer: answer,
      evaluation: evaluation,
      aiReply: aiReply
    });

    await saveCurrentSession();
    updateSessionScoreHistory();

  } catch (e) {
    console.error("Evaluation error:", e);
    alert(e.message || "An error occurred during evaluation. Please try again.");
  } finally {
    btn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4 text-cyan-300 mr-2"></i> Submit Answer & Receive AI Coaching`;
    btn.disabled = false;
    lucide.createIcons();
  }
}

function renderEvaluationResults(evalData, aiReply) {
  const panel = document.getElementById("evaluationResultsPanel");
  panel.classList.remove("hidden");

  // ── 1. AI Validation Verdict Banner ────────────────────────────────────────
  const verdict = aiReply.validation_verdict || "";
  const verdictBanner = document.getElementById("validationVerdictBanner");
  verdictBanner.classList.remove("hidden");

  const verdictConfig = {
    "Strong / Correct":          { icon: "✅", color: "bg-emerald-500/10 border-emerald-500/30", label: "Strong & Correct", desc: "Excellent! Your answer demonstrates solid technical understanding." },
    "Factually Incorrect":       { icon: "❌", color: "bg-rose-500/10 border-rose-500/30",    label: "Factually Incorrect", desc: "The AI detected a factual error. Review the exemplar answer below." },
    "Creative / Unconventional": { icon: "💡", color: "bg-amber-500/10 border-amber-500/30",  label: "Creative / Unconventional", desc: "Interesting angle! The interviewer is engaging with your unique perspective." },
    "Partially Correct":         { icon: "⚡", color: "bg-cyan-500/10 border-cyan-500/30",    label: "Partially Correct", desc: "Good foundation, but key aspects are missing or incomplete." },
    "Off-Topic / Vague":         { icon: "🌫️", color: "bg-slate-500/10 border-slate-500/30",  label: "Off-Topic / Vague", desc: "The response needs to be more focused and relevant to the question." },
  };
  const vc = verdictConfig[verdict] || { icon: "🤖", color: "bg-purple-500/10 border-purple-500/30", label: verdict || "Feedback ready", desc: "Review the feedback and rubric evidence." };
  verdictBanner.className = `flex items-center gap-3 p-3.5 rounded-xl border transition-all ${vc.color}`;
  document.getElementById("verdictIcon").innerText = vc.icon;
  document.getElementById("verdictLabel").innerText = vc.label;
  document.getElementById("verdictDescription").innerText = vc.desc;

  // ── 2. Running Subtitle / Typewriter Feedback ───────────────────────────────
  const feedbackBox = document.getElementById("conversationalFeedbackBox");
  feedbackBox.classList.remove("hidden");
  // Set persona avatar in the feedback box
  const currentP = state.personas[state.currentPersonaKey] || {};
  document.getElementById("subtitlePersonaAvatar").innerText = currentP.avatar || "👩‍🔬";

  const feedbackText = aiReply.conversational_feedback || aiReply.acknowledgment || "";
  typewriterEffect(feedbackText, "conversationalFeedbackText", 22);

  // ── 3. Overall Score ────────────────────────────────────────────────────────
  const score = Number.isFinite(evalData.overall_score) ? Math.round(evalData.overall_score) : null;
  document.getElementById("overallScoreDisplay").innerText = score === null ? "—" : score;
  const scoreMethod = document.getElementById("scoreMethodText");
  if (evalData.ai_score_components) {
    const components = evalData.ai_score_components;
    scoreMethod.innerText = `${evalData.score_method} Accuracy ${components.technical_accuracy}, completeness ${components.completeness}, clarity ${components.clarity}. ${evalData.ai_score_rationale || ""}`;
  } else {
    scoreMethod.innerText = evalData.score_method || "Score method unavailable.";
  }
  document.getElementById("scoreScaleLabel").classList.toggle("hidden", score === null);
  const ratingBadge = document.getElementById("scoreRatingBadge");
  if (score === null) {
    ratingBadge.className = "ml-2 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-500/10 text-slate-300 border border-slate-500/20";
    ratingBadge.innerText = "Unscored: no rubric";
  } else if (score >= 80) {
    ratingBadge.className = "ml-2 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
    ratingBadge.innerText = "🌟 Exceptional / Senior";
  } else if (score >= 60) {
    ratingBadge.className = "ml-2 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20";
    ratingBadge.innerText = "✅ Strong & Solid";
  } else {
    ratingBadge.className = "ml-2 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20";
    ratingBadge.innerText = "⚠️ Needs Elaboration";
  }

  // ── 4. WPM & Fillers & STAR ─────────────────────────────────────────────────
  const fluency = evalData.fluency || {};
  document.getElementById("evalWPMDisplay").innerText =
    fluency.estimated_wpm === null || fluency.estimated_wpm === undefined
      ? "Not measured" : `${fluency.estimated_wpm} WPM`;
  document.getElementById("evalFillerDisplay").innerText = fluency.filler_count || 0;
  document.getElementById("evalSTARDisplay").innerText = `${Math.round(evalData.star?.star_score || 0)}%`;

  // ── 5. Render STAR Sentences ─────────────────────────────────────────────────
  const starContainer = document.getElementById("starSentencesContainer");
  starContainer.innerHTML = "";
  const tagged = evalData.star?.tagged_sentences || [];
  if (tagged.length === 0) {
    starContainer.innerHTML = `<span class="text-slate-400 italic">Could not deconstruct sentences.</span>`;
  } else {
    tagged.forEach(item => {
      const p = document.createElement("p");
      p.className = "leading-relaxed";
      let badgeClass = "badge-general";
      if (item.tag === "Situation") badgeClass = "badge-situation";
      else if (item.tag === "Task") badgeClass = "badge-task";
      else if (item.tag === "Action") badgeClass = "badge-action";
      else if (item.tag === "Result") badgeClass = "badge-result";
      const badge = document.createElement("span");
      badge.className = `inline-block text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5 uppercase ${badgeClass}`;
      badge.textContent = (item.tags || [item.tag]).join(" / ");
      const sentence = document.createElement("span");
      sentence.className = "text-slate-200";
      sentence.textContent = item.sentence;
      p.append(badge, sentence);
      starContainer.appendChild(p);
    });
  }

  // ── 6. Interviewer Response ──────────────────────────────────────────────────
  document.getElementById("interviewerAckText").innerText = `"${aiReply.acknowledgment}"`;
  document.getElementById("interviewerFollowUpText").innerText = `"${aiReply.follow_up_question}"`;
  document.getElementById("modelExemplarText").innerText = aiReply.model_exemplar_answer;
  const providerNote = aiReply.ai_mode === "offline"
    ? `Offline linguistic feedback (not an LLM).`
    : `LLM feedback via ${aiReply.provider_used || "configured provider"}.`;
  document.getElementById("verdictDescription").innerText += ` ${providerNote}`;

  // Scroll to results panel smoothly
  panel.scrollIntoView({ behavior: 'smooth' });
}

function updateSessionScoreHistory() {
  const container = document.getElementById("sessionHistoryList");
  container.innerHTML = "";

  if (state.sessionHistory.length === 0) {
    container.innerHTML = `<div class="text-slate-500 italic text-[11px]">No questions answered in this session yet.</div>`;
    document.getElementById("sessionAvgScoreLabel").innerText = "Avg: -- / 100";
    return;
  }

  let totalScore = 0;
  let scoredCount = 0;
  state.sessionHistory.forEach((item, idx) => {
    const rawScore = item.evaluation?.overall_score;
    const sc = Number.isFinite(rawScore) ? Math.round(rawScore) : null;
    if (sc !== null) {
      totalScore += sc;
      scoredCount++;
    }
    const row = document.createElement("div");
    row.className = "flex items-center justify-between py-1 border-b border-white/5";
    row.innerHTML = `
      <span class="truncate max-w-[170px] text-slate-300">Q${idx + 1}: ${item.question?.category || 'Tech'}</span>
      <span class="font-mono font-bold text-emerald-400">${sc === null ? "Not scored" : `${sc} pts`}</span>
    `;
    container.appendChild(row);
  });

  const avg = scoredCount ? Math.round(totalScore / scoredCount) : null;
  document.getElementById("sessionAvgScoreLabel").innerText =
    avg === null ? "Avg: not scored" : `Avg: ${avg} / 100`;
}

// --- Resume & JD Tailoring ---
function setupDragAndDrop() {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("resumeFileInput");
  if (!dropZone || !fileInput) return;

  dropZone.addEventListener("click", () => fileInput.click());

  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.add("border-purple-500", "bg-purple-950/20");
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.remove("border-purple-500", "bg-purple-950/20");
    }, false);
  });

  dropZone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;
      onFileSelected(fileInput);
    }
  });
}

function onFileSelected(input) {
  if (input.files && input.files[0]) {
    const fn = input.files[0].name;
    const label = document.getElementById("selectedFileName");
    label.innerText = `Selected: ${fn}`;
    label.classList.remove("hidden");
  }
}

async function loadSampleResume(type) {
  const sampleName = type === 'nlp' ? 'Priya Sharma (NLP)' : 'Alex Chen (SWE)';
  await parseResumePayload({ sample_name: sampleName });
}

async function parseAndGenerateTailoredQuestions() {
  const fileInput = document.getElementById("resumeFileInput");
  const jdText = document.getElementById("jdInput").value.trim();

  const formData = new FormData();
  if (fileInput.files && fileInput.files[0]) {
    const resumeFile = fileInput.files[0];
    if (!/\.(pdf|txt)$/i.test(resumeFile.name)) {
      alert("Please select a PDF or TXT resume.");
      return;
    }
    if (resumeFile.size > 5 * 1024 * 1024) {
      alert("Resume upload exceeds the 5 MB limit.");
      return;
    }
    formData.append("file", resumeFile);
  } else {
    // Default to NLP sample if empty
    formData.append("sample_name", "Priya Sharma (NLP)");
  }
  if (jdText) {
    formData.append("job_description", jdText);
  }

  await parseResumePayload(formData);
}

async function parseResumePayload(payload) {
  try {
    let res;
    if (payload instanceof FormData) {
      res = await fetch("/api/resume/parse", { method: "POST", body: payload });
    } else {
      const fd = new FormData();
      Object.keys(payload).forEach(k => fd.append(k, payload[k]));
      res = await fetch("/api/resume/parse", { method: "POST", body: fd });
    }
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `Resume analysis failed (${res.status}).`);

    // Render Extracted Skills
    const skillsContainer = document.getElementById("extractedSkillsContainer");
    skillsContainer.innerHTML = "";
    const skillsObj = data.parsed_skills || {};
    let count = 0;
    Object.keys(skillsObj).forEach(cat => {
      skillsObj[cat].forEach(skill => {
        const badge = document.createElement("span");
        badge.className = "text-[11px] font-mono bg-purple-500/10 text-purple-300 px-2 py-0.5 rounded-md border border-purple-500/20";
        badge.innerText = skill;
        skillsContainer.appendChild(badge);
        count++;
      });
    });

    if (count === 0) {
      skillsContainer.innerHTML = `<span class="text-slate-400 italic text-xs">No specific skill keywords detected.</span>`;
    }

    // Render Tailored Questions
    const matchContainer = document.getElementById("jobMatchContainer");
    matchContainer.replaceChildren();
    if (data.job_match) {
      matchContainer.classList.remove("hidden");
      const title = document.createElement("div");
      title.className = "text-xs font-semibold text-slate-300";
      title.textContent = `Job skill coverage: ${data.job_match.coverage_pct ?? "Not scored"}${data.job_match.coverage_pct === null ? "" : "%"}`;
      const skills = document.createElement("p");
      skills.className = "text-[11px] text-slate-400";
      skills.textContent = `Matched: ${data.job_match.matched_skills.join(", ") || "none detected"} · Gaps: ${data.job_match.missing_skills.join(", ") || "none detected"}`;
      matchContainer.append(title, skills);
    } else {
      matchContainer.classList.add("hidden");
    }

    const qContainer = document.getElementById("tailoredQuestionsContainer");
    qContainer.innerHTML = "";
    state.tailoredQuestions = data.tailored_questions || [];

    if (state.tailoredQuestions.length > 0) {
      document.getElementById("loadTailoredToStudioBtn").classList.remove("hidden");
      state.tailoredQuestions.forEach((q, idx) => {
        const card = document.createElement("div");
        card.className = "p-3 bg-[#0E131F] rounded-xl border border-white/10 space-y-1.5";
        const metadata = document.createElement("div");
        metadata.className = "flex items-center justify-between text-[11px]";
        const category = document.createElement("span");
        category.className = "text-purple-400 font-semibold uppercase";
        category.textContent = q.category;
        const difficulty = document.createElement("span");
        difficulty.className = "text-cyan-400";
        difficulty.textContent = q.difficulty;
        metadata.append(category, difficulty);
        const questionText = document.createElement("p");
        questionText.className = "text-xs text-slate-100 font-medium";
        questionText.textContent = `${idx + 1}. ${q.question}`;
        card.append(metadata, questionText);
        qContainer.appendChild(card);
      });
    }

  } catch (e) {
    console.error("Resume parsing error:", e);
    alert(e.message || "Error parsing resume. Please ensure file format is PDF or TXT.");
  }
}

function loadTailoredQuestionsIntoStudio() {
  if (state.tailoredQuestions.length === 0) return;
  state.activeQuestions = state.tailoredQuestions;
  state.currentQIndex = 0;
  state.sessionHistory = [];
  state.followUpAsked = new Set();
  state.sessionId = createSessionId();
  displayCurrentQuestion();
  switchTab("studio");
  alert("✨ Tailored questions loaded into your Live Studio! Start answering question 1.");
}

// --- Analytics Dashboard & Charts ---
function renderAnalyticsDashboard() {
  const history = state.sessionHistory;
  if (history.length === 0) {
    document.getElementById("analyticsAvgScore").innerText = "--";
    document.getElementById("analyticsAvgSTAR").innerText = "--%";
    document.getElementById("analyticsAvgWPM").innerText = "-- WPM";
    document.getElementById("analyticsTotalFillers").innerText = "0";
    return;
  }

  const scores = history.map(h => h.evaluation.overall_score).filter(Number.isFinite);
  const stars = history
    .filter(h => h.evaluation.score_components?.star_structure !== undefined)
    .map(h => h.evaluation.score_components.star_structure);
  const wpms = history.map(h => h.evaluation.fluency?.estimated_wpm).filter(Number.isFinite);
  const fluencyScores = history.map(h => h.evaluation.fluency?.fluency_score).filter(Number.isFinite);
  const clarityScores = history.map(h => h.evaluation.communication_clarity_score).filter(Number.isFinite);
  const relevanceScores = history
    .map(h => h.evaluation.score_components?.answer_relevance)
    .filter(Number.isFinite);
  const fillers = history.map(h => h.evaluation.fluency?.filler_count || 0);

  const average = values => values.length
    ? values.reduce((a, b) => a + b, 0) / values.length : null;
  const avgScore = average(scores);
  const avgStar = average(stars);
  const avgWpm = average(wpms);
  const totalFillers = fillers.reduce((a, b) => a + b, 0);

  document.getElementById("analyticsAvgScore").innerText =
    avgScore === null ? "Not scored" : `${avgScore.toFixed(0)} / 100`;
  document.getElementById("analyticsAvgSTAR").innerText =
    avgStar === null ? "N/A" : `${avgStar.toFixed(0)}%`;
  document.getElementById("analyticsAvgWPM").innerText =
    avgWpm === null ? "Not measured" : `${avgWpm.toFixed(0)} WPM`;
  document.getElementById("analyticsTotalFillers").innerText = totalFillers;

  renderRadarChart({
    relevance: average(relevanceScores),
    star: avgStar,
    fluency: average(fluencyScores),
    clarity: average(clarityScores),
    wpm: avgWpm
  });
  // Render Filler Bar Chart
  renderFillerBarChart();
}

function renderRadarChart(metrics) {
  const ctx = document.getElementById("competencyRadarChart");
  if (!ctx) return;

  if (state.radarChart) state.radarChart.destroy();

  let paceScore = null;
  if (metrics.wpm !== null) {
    paceScore = metrics.wpm < 120
      ? Math.max(0, 100 - (120 - metrics.wpm) * 0.25)
      : metrics.wpm > 165
        ? Math.max(0, 100 - (metrics.wpm - 165) * 0.25)
        : 100;
  }

  state.radarChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Answer relevance', 'STAR structure', 'Fluency markers', 'Communication clarity', 'Speaking pace'],
      datasets: [{
        label: 'Measured indicators',
        data: [metrics.relevance, metrics.star, metrics.fluency, metrics.clarity, paceScore],
        backgroundColor: 'rgba(139, 92, 246, 0.25)',
        borderColor: '#8B5CF6',
        pointBackgroundColor: '#06B6D4',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#06B6D4',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
          grid: { color: 'rgba(255, 255, 255, 0.08)' },
          pointLabels: {
            color: '#94A3B8',
            font: { size: 11, family: 'Plus Jakarta Sans' }
          },
          ticks: { display: false, min: 0, max: 100 }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function renderFillerBarChart() {
  const ctx = document.getElementById("fillerBarChart");
  if (!ctx) return;

  if (state.fillerChart) state.fillerChart.destroy();

  // Aggregate fillers
  const counts = { 'um': 0, 'uh': 0, 'like': 0, 'basically': 0, 'you know': 0, 'actually': 0 };
  state.sessionHistory.forEach(h => {
    const b = h.evaluation.fluency?.filler_breakdown || {};
    Object.keys(b).forEach(k => {
      counts[k] = (counts[k] || 0) + b[k];
    });
  });

  const labels = Object.keys(counts);
  const data = Object.values(counts);

  state.fillerChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Occurrences',
        data: data,
        backgroundColor: 'rgba(244, 63, 94, 0.6)',
        borderColor: '#F43F5E',
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.08)' },
          ticks: { color: '#94A3B8', stepSize: 1 }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#F1F5F9' }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

async function downloadReport(format) {
  if (state.sessionHistory.length === 0) {
    alert("Please complete at least one question before downloading an assessment report.");
    return;
  }

  const candidateName = document.getElementById("candidateNameInput").value || "Candidate";
  const scores = state.sessionHistory.map(h => h.evaluation.overall_score).filter(Number.isFinite);
  const stars = state.sessionHistory
    .filter(h => h.evaluation.score_components?.star_structure !== undefined)
    .map(h => h.evaluation.score_components.star_structure);
  const wpms = state.sessionHistory.map(h => h.evaluation.fluency?.estimated_wpm).filter(Number.isFinite);
  const fillers = state.sessionHistory.map(h => h.evaluation.fluency?.filler_count || 0);
  const average = values => values.length
    ? values.reduce((a, b) => a + b, 0) / values.length : null;

  const payload = {
    candidate_name: candidateName,
    persona_name: state.currentPersonaKey,
    session_results: state.sessionHistory,
    overall_summary: {
      average_score: average(scores),
      average_star: average(stars),
      average_wpm: average(wpms),
      total_fillers: fillers.reduce((a, b) => a + b, 0)
    }
  };

  const endpoint = format === 'markdown' ? '/api/report/markdown' : '/api/report/json';
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (format === 'markdown') {
    const data = await res.json();
    const blob = new Blob([data.markdown], { type: 'text/markdown' });
    triggerDownload(blob, `AI_Interview_Report_${candidateName.replace(/\s+/g, '_')}.md`);
  } else {
    const data = await res.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    triggerDownload(blob, `AI_Interview_Analytics_${candidateName.replace(/\s+/g, '_')}.json`);
  }
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// --- Question Bank Explorer ---
async function loadQuestionBank() {
  try {
    const res = await fetch("/api/questions?limit=100");
    const qs = await res.json();
    renderBankQuestions(qs);
  } catch (e) {
    console.error("Bank load error:", e);
  }
}

async function onBankSearch() {
  const query = document.getElementById("bankSearchInput").value;
  const cat = document.getElementById("bankCategorySelect").value;
  const diff = document.getElementById("bankDifficultySelect").value;

  const url = `/api/questions?search=${encodeURIComponent(query)}&category=${encodeURIComponent(cat)}&difficulty=${encodeURIComponent(diff)}&limit=60`;
  const res = await fetch(url);
  const qs = await res.json();
  renderBankQuestions(qs);
}

function renderBankQuestions(qs) {
  const grid = document.getElementById("bankQuestionsGrid");
  grid.innerHTML = "";
  document.getElementById("bankTotalBadge").innerText = `${qs.length} Questions Displayed`;

  if (qs.length === 0) {
    grid.innerHTML = `<div class="col-span-2 text-center text-slate-500 py-8">No questions match your filter criteria.</div>`;
    return;
  }

  qs.forEach(q => {
    const card = document.createElement("div");
    card.className = "glass-card-interactive p-4 border border-white/10 flex flex-col justify-between";
    card.innerHTML = `
      <div class="space-y-2">
        <div class="flex items-center justify-between text-[11px]">
          <span class="text-purple-400 font-semibold uppercase">${q.category}</span>
          <span class="text-cyan-400 font-mono">${q.difficulty}</span>
        </div>
        <p class="text-xs text-white font-semibold leading-relaxed">${q.question}</p>
        <div class="flex flex-wrap gap-1 mt-2">
          ${(q.keywords || []).slice(0, 4).map(k => `<span class="text-[10px] bg-white/5 text-slate-400 px-1.5 py-0.5 rounded">${k}</span>`).join('')}
        </div>
      </div>
      <div class="pt-3 mt-3 border-t border-white/5 flex justify-end">
        <button onclick="practiceQuestionDirectly(${JSON.stringify(q).replace(/"/g, '&quot;')})" class="text-xs text-cyan-400 hover:text-white flex items-center gap-1 font-semibold">
          <span>Practice This</span>
          <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
        </button>
      </div>
    `;
    grid.appendChild(card);
  });
  lucide.createIcons();
}

function practiceQuestionDirectly(q) {
  state.activeQuestions = [q];
  state.currentQIndex = 0;
  state.sessionHistory = [];
  state.followUpAsked = new Set();
  state.sessionId = createSessionId();
  displayCurrentQuestion();
  switchTab("studio");
}

// --- Computational Linguistics Lab ---
function loadLabSampleText() {
  document.getElementById("labInputText").value =
    "At my previous fintech startup, our payment microservice experienced high latency during flash sales. " +
    "My objective was to reduce API response latency below 100 milliseconds without increasing infrastructure costs. " +
    "I profiled the database queries with EXPLAIN ANALYZE, added composite B-Tree indexes, and deployed an asynchronous Celery queue with Redis. " +
    "As a result, API response times dropped by 64% and shopping cart abandonment decreased by 22%.";
}

async function runLabAnalysis() {
  const text = document.getElementById("labInputText").value.trim();
  if (!text) {
    alert("Please enter a paragraph to analyze.");
    return;
  }

  try {
    const res = await fetch("/api/nlp/playground", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    });
    const data = await res.json();

    const ling = data.linguistics || {};
    document.getElementById("labFleschDisplay").innerText = ling.flesch_reading_ease || "--";
    document.getElementById("labFogDisplay").innerText = ling.gunning_fog_index || "--";
    document.getElementById("labTTRDisplay").innerText = ling.lexical_diversity_ttr || "--";
    document.getElementById("labHapaxDisplay").innerText = ling.hapax_legomena_ratio || "--";
    document.getElementById("labAvgSentDisplay").innerText = `${ling.avg_sentence_length || '--'} wps`;
    document.getElementById("labConfidenceDisplay").innerText = data.tone?.tone_label || "--";

    // Sentence classifier
    const container = document.getElementById("labSentencesContainer");
    container.innerHTML = "";
    (data.star?.tagged_sentences || []).forEach(item => {
      const p = document.createElement("p");
      p.className = "leading-relaxed";
      let bClass = "badge-general";
      if (item.tag === "Situation") bClass = "badge-situation";
      else if (item.tag === "Task") bClass = "badge-task";
      else if (item.tag === "Action") bClass = "badge-action";
      else if (item.tag === "Result") bClass = "badge-result";
      p.innerHTML = `<span class="inline-block text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5 uppercase ${bClass}">${item.tag}</span> <span class="text-slate-200">${item.sentence}</span>`;
      container.appendChild(p);
    });

  } catch (e) {
    console.error("Lab analysis error:", e);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// ★ FEATURE 1: AI Answer Validation — Typewriter / Running Subtitle Effect
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Animates text into element character-by-character, like a running subtitle.
 * @param {string} text - Text to type out
 * @param {string} elementId - ID of the DOM element to type into
 * @param {number} speed - Milliseconds per character (default 22ms ≈ smooth subtitle pace)
 */
function typewriterEffect(text, elementId, speed = 22) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const content = String(text);
  const textNode = document.createTextNode("");
  el.replaceChildren(textNode);

  // Show the "typing" dots indicator
  const typingDot = document.getElementById("subtitleTypingDot");
  if (typingDot) typingDot.classList.remove("hidden");

  let i = 0;
  function tick() {
    if (i < content.length) {
      textNode.appendData(content[i++]);
      setTimeout(tick, speed);
    } else {
      // Done — hide typing indicator
      if (typingDot) typingDot.classList.add("hidden");
    }
  }
  tick();
}

// ═══════════════════════════════════════════════════════════════════════════════
// ★ FEATURE 2: AI Connectivity Status — Live Badge & Detail Panel
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Calls the backend /api/ai/connectivity endpoint and updates the header badge
 * and the detail panel with live values.
 */
async function checkAIConnectivity() {
  // Show "checking" state
  const dot = document.getElementById("connStatusDot");
  const label = document.getElementById("connStatusLabel");
  if (dot) dot.className = "w-2 h-2 rounded-full bg-slate-500 animate-pulse transition-colors";
  if (label) label.innerText = "Checking AI...";
  const recheckSpinner = document.getElementById("recheckSpinner");
  if (recheckSpinner) recheckSpinner.classList.remove("hidden");

  try {
    const res = await fetch("/api/ai/connectivity");
    const data = await res.json();

    const online = data.online === true;
    const fallback = data.fallback_ready === true;
    const latency = data.latency_ms ? `${Math.round(data.latency_ms)}ms` : "—";

    // Update badge dot colour
    const dotColor = online ? "bg-emerald-400" : (fallback ? "bg-amber-400" : "bg-rose-400");
    const dotPulse = online ? "animate-pulse" : "";
    if (dot) dot.className = `w-2 h-2 rounded-full ${dotColor} ${dotPulse} transition-colors`;

    // Update badge label
    const labelText = online
        ? `${data.provider || "Configured provider"} · ${latency}`
        : (data.ai_mode === "configured"
          ? "Provider configured · not yet verified"
          : (fallback ? "Offline feedback · not an LLM" : "No provider available"));
    if (label) {
      label.innerText = labelText;
      label.className = online ? "text-emerald-300 transition-colors" : (fallback ? "text-amber-300 transition-colors" : "text-rose-300 transition-colors");
    }

    // Update latency badge
    const latencyBadge = document.getElementById("connLatencyBadge");
    if (latencyBadge && online) {
      latencyBadge.classList.remove("hidden");
      latencyBadge.innerText = latency;
    }

    // Update detail panel
    const panelDot = document.getElementById("connPanelDot");
    if (panelDot) panelDot.className = `w-2.5 h-2.5 rounded-full ${dotColor} ${dotPulse}`;
    const setPanel = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; };
    setPanel("connProviderLabel",  data.provider  || "—");
    setPanel("connModelLabel",     data.model     || "—");
    setPanel("connLatencyLabel",   online ? latency : "—");
    setPanel("connStatusDetail",   data.status_text || (online ? "Connected" : "Unavailable"));
    setPanel("connFallbackLabel",  fallback ? "✅ Local fallback ready" : "ℹ️ No local fallback");

  } catch (err) {
    // Network failure
    if (dot) dot.className = "w-2 h-2 rounded-full bg-rose-400 transition-colors";
    if (label) { label.innerText = "AI Unreachable"; label.className = "text-rose-300 transition-colors"; }
  } finally {
    if (recheckSpinner) recheckSpinner.classList.add("hidden");
  }
}

function toggleConnectivityPanel() {
  const panel = document.getElementById("connectivityPanel");
  if (!panel) return;
  panel.classList.toggle("hidden");
}

// ═══════════════════════════════════════════════════════════════════════════════
// ★ FEATURE 3: Custom Interviewer — Create / AI-Generate / Delete
// ═══════════════════════════════════════════════════════════════════════════════

function openCreatePersonaModal() {
  // Clear all form fields
  ["newPersonaName","newPersonaRole","newPersonaTone","newPersonaDesc","newPersonaFocus","personaGenPrompt"]
    .forEach(id => { const el = document.getElementById(id); if (el) el.value = ""; });
  const avatar = document.getElementById("newPersonaAvatar");
  if (avatar) avatar.value = "🧑‍🏫";
  const status = document.getElementById("aiGenStatus");
  if (status) { status.innerText = ""; status.classList.add("hidden"); }
  document.getElementById("createPersonaModal").classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

function closeCreatePersonaModal() {
  document.getElementById("createPersonaModal").classList.add("hidden");
  document.body.style.overflow = "";
}

function onModalBackdropClick(e) {
  if (e.target === document.getElementById("createPersonaModal")) {
    closeCreatePersonaModal();
  }
}

/**
 * Requests a local heuristic persona draft and fills the form.
 */
async function aiGeneratePersona() {
  const prompt = document.getElementById("personaGenPrompt").value.trim();
  if (!prompt) {
    showToast("⚠️ Please enter a description for the AI to generate from.", "amber");
    return;
  }

  const btn = document.getElementById("aiGenBtn");
  const spinner = document.getElementById("aiGenSpinner");
  const btnText = document.getElementById("aiGenBtnText");
  const status = document.getElementById("aiGenStatus");

  btn.disabled = true;
  spinner.classList.remove("hidden");
  btnText.innerText = "Generating...";
  status.innerText = "Drafting a local heuristic persona...";
  status.classList.remove("hidden");

  try {
    const res = await fetch("/api/personas/ai-generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || `Draft generation failed (${res.status}).`);

    // Fill in form fields from AI response
    const set = (id, val) => { const el = document.getElementById(id); if (el && val) el.value = val; };
    set("newPersonaName",   data.name);
    set("newPersonaRole",   data.role);
    set("newPersonaAvatar", data.avatar);
    set("newPersonaTone",   data.tone);
    set("newPersonaDesc",   data.description);
    set("newPersonaFocus",  data.special_focus);

    // Set domain dropdown if matching
    if (data.default_domain) {
      const domSel = document.getElementById("newPersonaDomain");
      const opts = Array.from(domSel.options);
      const match = opts.find(o => o.value.toLowerCase().includes(data.default_domain.toLowerCase().split(" ")[0]));
      if (match) domSel.value = match.value;
    }

    status.innerText = "✅ Local heuristic draft filled in (not an LLM). Review and save.";
    status.className = "text-[11px] text-emerald-400";

  } catch (err) {
    console.error("AI generate persona error:", err);
    status.innerText = `❌ Generation failed: ${err.message || "Network error"}. Try again or fill manually.`;
    status.className = "text-[11px] text-rose-400";
  } finally {
    btn.disabled = false;
    spinner.classList.add("hidden");
    btnText.innerText = "Draft";
  }
}

/**
 * Reads the create-persona form, POSTs to /api/personas/create, and reloads personas.
 */
async function saveCustomPersona() {
  const name    = document.getElementById("newPersonaName").value.trim();
  const role    = document.getElementById("newPersonaRole").value.trim();
  const avatar  = document.getElementById("newPersonaAvatar").value.trim() || "🧑‍🏫";
  const tone    = document.getElementById("newPersonaTone").value.trim() || "Professional & Analytical";
  const desc    = document.getElementById("newPersonaDesc").value.trim() || "Custom AI interviewer.";
  const domain  = document.getElementById("newPersonaDomain").value;
  const focus   = document.getElementById("newPersonaFocus").value.trim();

  if (!name || !role) {
    showToast("⚠️ Interviewer Name and Role are required.", "amber");
    return;
  }

  const saveBtn = document.getElementById("savePersonaBtn");
  const spinner = document.getElementById("savePersonaSpinner");
  saveBtn.disabled = true;
  spinner.classList.remove("hidden");

  try {
    const payload = { name, role, avatar, tone, description: desc, domain, special_focus: focus };
    const res = await fetch("/api/personas/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || "Failed to save.");

    closeCreatePersonaModal();
    await loadPersonas();

    // Auto-select the newly created persona in the dropdown
    const newKey = `${name} (Custom)`;
    const select = document.getElementById("personaSelect");
    const opt = Array.from(select.options).find(o => o.value === newKey || o.value.startsWith(name));
    if (opt) { select.value = opt.value; state.currentPersonaKey = opt.value; updatePersonaDisplay(); }

    showToast(`✅ "${name}" has been created and selected!`, "emerald");

  } catch (err) {
    console.error("Save persona error:", err);
    showToast(`❌ Save failed: ${err.message}`, "rose");
  } finally {
    saveBtn.disabled = false;
    spinner.classList.add("hidden");
  }
}

/**
 * Sends DELETE to /api/personas/{name}. On success reloads the persona list.
 */
async function deletePersona(personaKey) {
  if (!confirm(`Delete the custom interviewer "${personaKey.split(" (")[0]}"? This cannot be undone.`)) return;
  try {
    const res = await fetch(`/api/personas/${encodeURIComponent(personaKey)}`, { method: "DELETE" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Could not delete.");

    // If deleted persona was active, reset to first built-in
    if (state.currentPersonaKey === personaKey) {
      const firstBuiltIn = Object.keys(state.personas).find(k => state.personas[k].built_in !== false);
      state.currentPersonaKey = firstBuiltIn || Object.keys(state.personas)[0];
    }
    await loadPersonas();
    // Re-sync select to current persona
    const select = document.getElementById("personaSelect");
    if (select) select.value = state.currentPersonaKey;
    updatePersonaDisplay();
    showToast(`🗑️ Interviewer deleted successfully.`, "slate");

  } catch (err) {
    console.error("Delete persona error:", err);
    showToast(`❌ Delete failed: ${err.message}`, "rose");
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// ★ UTILITY: Toast Notifications
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Shows a dismissible toast at bottom-right corner.
 * @param {string} message - HTML-safe text
 * @param {string} color   - "emerald" | "amber" | "rose" | "slate" | "purple"
 */
function showToast(message, color = "purple") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const colorMap = {
    emerald: "bg-emerald-950/90 border-emerald-500/40 text-emerald-300",
    amber:   "bg-amber-950/90  border-amber-500/40  text-amber-300",
    rose:    "bg-rose-950/90   border-rose-500/40   text-rose-300",
    slate:   "bg-slate-900/90  border-slate-500/40  text-slate-300",
    purple:  "bg-purple-950/90 border-purple-500/40 text-purple-300",
  };

  const toast = document.createElement("div");
  toast.className = `pointer-events-auto flex items-center gap-2 px-4 py-2.5 rounded-xl border text-xs font-semibold shadow-xl
    transition-all opacity-0 translate-y-2 ${colorMap[color] || colorMap.purple}`;
  toast.innerText = message;
  container.appendChild(toast);

  // Animate in
  requestAnimationFrame(() => {
    toast.style.opacity = "1";
    toast.style.transform = "translateY(0)";
    toast.style.transition = "all 0.3s ease";
  });

  // Auto-dismiss after 4s
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(4px)";
    setTimeout(() => toast.remove(), 350);
  }, 4000);
}
