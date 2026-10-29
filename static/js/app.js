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
  tailoredQuestions: [],
  isRecording: false,
  recognition: null,
  recordingStartTime: null,
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
  } catch (e) {
    console.error("Failed to load personas:", e);
  }
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
      displayCurrentQuestion();
      document.getElementById("evaluationResultsPanel").classList.add("hidden");
      updateSessionScoreHistory();
    }
  } catch (e) {
    console.error("Error starting session:", e);
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
  document.getElementById("wpmEstimateLive").innerText = "0";
  document.getElementById("evaluationResultsPanel").classList.add("hidden");
}

function nextQuestion() {
  state.currentQIndex++;
  displayCurrentQuestion();
}

function skipQuestion() {
  if (confirm("Skip this question and move to the next?")) {
    nextQuestion();
  }
}

function onSessionCompleted() {
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
    let finalTrans = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTrans += event.results[i][0].transcript + ' ';
      }
    }
    const txtArea = document.getElementById("answerTranscriptInput");
    if (finalTrans) {
      txtArea.value += finalTrans;
      updateLiveTimerAndStats();
    }
  };

  rec.onerror = (e) => {
    console.warn("Speech recognition warning:", e.error);
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
  state.isRecording = false;
  updateRecordingUI(false);
  if (state.timerInterval) clearInterval(state.timerInterval);
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

  let seconds = 0;
  if (state.recordingStartTime && state.isRecording) {
    seconds = Math.max(1, Math.floor((Date.now() - state.recordingStartTime) / 1000));
    const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
    const secs = String(seconds % 60).padStart(2, '0');
    document.getElementById("recordingTimer").innerText = `${mins}:${secs}`;
    
    // Calculate live WPM
    const wpm = Math.round((words / seconds) * 60);
    document.getElementById("wpmEstimateLive").innerText = wpm;
  }
}

function clearTranscript() {
  document.getElementById("answerTranscriptInput").value = "";
  document.getElementById("wordCountLive").innerText = "0";
  document.getElementById("wpmEstimateLive").innerText = "0";
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
        duration_seconds: state.recordingStartTime ? (Date.now() - state.recordingStartTime) / 1000 : null
      })
    });
    const evaluation = await evalRes.json();

    // 2. AI Conversational Follow-up
    const chatRes = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        persona_name: state.currentPersonaKey,
        candidate_answer: answer,
        current_question: currentQ,
        nlp_evaluation: evaluation
      })
    });
    const aiReply = await chatRes.json();

    // Render Results
    renderEvaluationResults(evaluation, aiReply);

    // Save into history
    state.sessionHistory.push({
      question: currentQ,
      answer: answer,
      evaluation: evaluation,
      aiReply: aiReply
    });

    updateSessionScoreHistory();

  } catch (e) {
    console.error("Evaluation error:", e);
    alert("An error occurred during evaluation. Please try again.");
  } finally {
    btn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4 text-cyan-300 mr-2"></i> Submit Answer & Receive AI Coaching`;
    btn.disabled = false;
    lucide.createIcons();
  }
}

function renderEvaluationResults(evalData, aiReply) {
  const panel = document.getElementById("evaluationResultsPanel");
  panel.classList.remove("hidden");

  // Overall Score
  const score = Math.round(evalData.overall_score || 0);
  document.getElementById("overallScoreDisplay").innerText = score;
  const ratingBadge = document.getElementById("scoreRatingBadge");
  if (score >= 80) {
    ratingBadge.className = "ml-2 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
    ratingBadge.innerText = "🌟 Exceptional / Senior";
  } else if (score >= 60) {
    ratingBadge.className = "ml-2 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20";
    ratingBadge.innerText = "✅ Strong & Solid";
  } else {
    ratingBadge.className = "ml-2 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20";
    ratingBadge.innerText = "⚠️ Needs Elaboration";
  }

  // WPM & Fillers & STAR
  const fluency = evalData.fluency || {};
  document.getElementById("evalWPMDisplay").innerText = `${fluency.estimated_wpm || 135} WPM`;
  document.getElementById("evalFillerDisplay").innerText = fluency.filler_count || 0;
  document.getElementById("evalSTARDisplay").innerText = `${Math.round(evalData.star?.star_score || 0)}%`;

  // Render STAR Sentences
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

      p.innerHTML = `<span class="inline-block text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5 uppercase ${badgeClass}">${item.tag}</span> <span class="text-slate-200">${item.sentence}</span>`;
      starContainer.appendChild(p);
    });
  }

  // Interviewer Response
  document.getElementById("interviewerAckText").innerText = `"${aiReply.acknowledgment || 'Good points discussed.'}"`;
  document.getElementById("interviewerFollowUpText").innerText = `"${aiReply.follow_up_question || 'How would you scale this in production?'}"`;
  document.getElementById("modelExemplarText").innerText = aiReply.model_exemplar_answer || "A senior answer clearly frames the background, action steps, and quantitative outcome.";

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
  state.sessionHistory.forEach((item, idx) => {
    const sc = Math.round(item.evaluation?.overall_score || 0);
    totalScore += sc;
    const row = document.createElement("div");
    row.className = "flex items-center justify-between py-1 border-b border-white/5";
    row.innerHTML = `
      <span class="truncate max-w-[170px] text-slate-300">Q${idx + 1}: ${item.question?.category || 'Tech'}</span>
      <span class="font-mono font-bold text-emerald-400">${sc} pts</span>
    `;
    container.appendChild(row);
  });

  const avg = Math.round(totalScore / state.sessionHistory.length);
  document.getElementById("sessionAvgScoreLabel").innerText = `Avg: ${avg} / 100`;
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
    formData.append("file", fileInput.files[0]);
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
    const qContainer = document.getElementById("tailoredQuestionsContainer");
    qContainer.innerHTML = "";
    state.tailoredQuestions = data.tailored_questions || [];

    if (state.tailoredQuestions.length > 0) {
      document.getElementById("loadTailoredToStudioBtn").classList.remove("hidden");
      state.tailoredQuestions.forEach((q, idx) => {
        const card = document.createElement("div");
        card.className = "p-3 bg-[#0E131F] rounded-xl border border-white/10 space-y-1.5";
        card.innerHTML = `
          <div class="flex items-center justify-between text-[11px]">
            <span class="text-purple-400 font-semibold uppercase">${q.category}</span>
            <span class="text-cyan-400">${q.difficulty}</span>
          </div>
          <p class="text-xs text-slate-100 font-medium">${idx + 1}. ${q.question}</p>
        `;
        qContainer.appendChild(card);
      });
    }

  } catch (e) {
    console.error("Resume parsing error:", e);
    alert("Error parsing resume. Please ensure file format is PDF or TXT.");
  }
}

function loadTailoredQuestionsIntoStudio() {
  if (state.tailoredQuestions.length === 0) return;
  state.activeQuestions = state.tailoredQuestions;
  state.currentQIndex = 0;
  state.sessionHistory = [];
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

  const scores = history.map(h => h.evaluation.overall_score || 0);
  const stars = history.map(h => h.evaluation.star?.star_score || 0);
  const wpms = history.map(h => h.evaluation.fluency?.estimated_wpm || 135);
  const fillers = history.map(h => h.evaluation.fluency?.filler_count || 0);

  const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  const avgStar = Math.round(stars.reduce((a, b) => a + b, 0) / stars.length);
  const avgWpm = Math.round(wpms.reduce((a, b) => a + b, 0) / wpms.length);
  const totalFillers = fillers.reduce((a, b) => a + b, 0);

  document.getElementById("analyticsAvgScore").innerText = `${avgScore} / 100`;
  document.getElementById("analyticsAvgSTAR").innerText = `${avgStar}%`;
  document.getElementById("analyticsAvgWPM").innerText = `${avgWpm} WPM`;
  document.getElementById("analyticsTotalFillers").innerText = totalFillers;

  // Render Radar Chart
  renderRadarChart(avgScore, avgStar, avgWpm, totalFillers);
  // Render Filler Bar Chart
  renderFillerBarChart();
}

function renderRadarChart(score, star, wpm, fillers) {
  const ctx = document.getElementById("competencyRadarChart");
  if (!ctx) return;

  if (state.radarChart) state.radarChart.destroy();

  const fluencyRating = Math.max(20, 100 - fillers * 5);
  const tempoRating = (wpm >= 120 && wpm <= 165) ? 95 : 65;

  state.radarChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Technical Depth', 'STAR Structure', 'Fluency Flow', 'Speaking Pace', 'Assertive Tone'],
      datasets: [{
        label: 'Candidate Competency',
        data: [score, star, fluencyRating, tempoRating, 80],
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
  const scores = state.sessionHistory.map(h => h.evaluation.overall_score || 0);
  const stars = state.sessionHistory.map(h => h.evaluation.star?.star_score || 0);
  const wpms = state.sessionHistory.map(h => h.evaluation.fluency?.estimated_wpm || 135);
  const fillers = state.sessionHistory.map(h => h.evaluation.fluency?.filler_count || 0);

  const payload = {
    candidate_name: candidateName,
    persona_name: state.currentPersonaKey,
    session_results: state.sessionHistory,
    overall_summary: {
      average_score: Math.round(scores.reduce((a, b) => a + b, 0) / scores.length),
      average_star: Math.round(stars.reduce((a, b) => a + b, 0) / stars.length),
      average_wpm: Math.round(wpms.reduce((a, b) => a + b, 0) / wpms.length),
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
