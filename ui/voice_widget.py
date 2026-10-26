"""
Interactive Voice Recording & Speech Recognition Widget.
Uses the HTML5 Web Speech API for real-time, low-latency, zero-cost speech-to-text.
"""

def render_voice_recorder_component(question_text: str = "", auto_listen: bool = False) -> str:
    """
    Renders an interactive HTML5 voice recorder card with real-time Web Speech recognition.
    """
    escaped_q = question_text.replace('"', '&quot;').replace("'", "&#39;")

    return f"""
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(96, 165, 250, 0.3); border-radius: 14px; padding: 18px; margin: 14px 0;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.4rem;">🎙️</span>
                <div>
                    <strong style="color: #F8FAFC; font-size: 1rem;">Live Voice Agent Studio</strong>
                    <div style="color: #94A3B8; font-size: 0.8rem;">Click 'Start Speaking' to transcribe your answer in real time</div>
                </div>
            </div>
            <div id="statusIndicator" style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; background: rgba(100, 116, 139, 0.2); color: #94A3B8;">
                <span id="statusDot" style="width: 8px; height: 8px; border-radius: 50%; background: #64748B;"></span>
                <span id="statusText">Ready</span>
            </div>
        </div>

        <!-- Controls -->
        <div style="display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;">
            <button id="listenBtn" onclick="readQuestionAloud()" style="background: #3B82F6; color: white; border: none; padding: 8px 14px; border-radius: 8px; cursor: pointer; font-size: 0.85rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                🔊 Listen to Question
            </button>
            <button id="toggleRecordBtn" onclick="toggleSpeechRecognition()" style="background: #10B981; color: white; border: none; padding: 8px 14px; border-radius: 8px; cursor: pointer; font-size: 0.85rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                🎤 Start Speaking
            </button>
            <button id="copyBtn" onclick="copyTranscript()" style="background: rgba(255, 255, 255, 0.1); color: #E2E8F0; border: 1px solid rgba(255, 255, 255, 0.2); padding: 8px 14px; border-radius: 8px; cursor: pointer; font-size: 0.85rem; font-weight: 500;">
                📋 Copy Text
            </button>
            <button id="clearBtn" onclick="clearTranscript()" style="background: transparent; color: #94A3B8; border: 1px solid rgba(148, 163, 184, 0.3); padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 0.85rem;">
                🗑️ Clear
            </button>
        </div>

        <!-- Live transcript box -->
        <textarea id="liveTranscript" rows="4" placeholder="Your transcribed speech will appear here automatically as you talk..." style="width: 100%; box-sizing: border-box; background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; color: #F1F5F9; font-family: inherit; font-size: 0.95rem; padding: 10px; resize: vertical;"></textarea>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; font-size: 0.8rem; color: #94A3B8;">
            <span id="wordCounter">Words: 0 | Duration: 0s</span>
            <span style="font-style: italic;">💡 You can paste or type into the main answer box below to submit!</span>
        </div>
    </div>

    <script>
    let recognition = null;
    let isRecording = false;
    let startTime = null;
    let timerInterval = null;
    const qText = "{escaped_q}";

    function readQuestionAloud() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(qText);
            utter.rate = 1.0;
            utter.pitch = 1.0;
            utter.lang = 'en-US';
            window.speechSynthesis.speak(utter);
        }} else {{
            alert("Speech synthesis is not supported on your browser.");
        }}
    }}

    function initSpeechRecognition() {{
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {{
            alert("Web Speech API is not supported in this browser. Please use Chrome, Edge, or Safari for voice input.");
            return null;
        }}
        const rec = new SpeechRec();
        rec.continuous = true;
        rec.interimResults = true;
        rec.lang = 'en-US';

        rec.onstart = function() {{
            isRecording = true;
            document.getElementById('statusText').innerText = "Listening...";
            document.getElementById('statusDot').style.background = "#EF4444";
            document.getElementById('toggleRecordBtn').innerText = "⏹️ Stop Recording";
            document.getElementById('toggleRecordBtn').style.background = "#EF4444";
            startTime = Date.now();
            timerInterval = setInterval(updateStats, 500);
        }};

        rec.onresult = function(event) {{
            let interimTranscript = '';
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {{
                if (event.results[i].isFinal) {{
                    finalTranscript += event.results[i][0].transcript + ' ';
                }} else {{
                    interimTranscript += event.results[i][0].transcript;
                }}
            }}
            const txtArea = document.getElementById('liveTranscript');
            if (finalTranscript) {{
                txtArea.value += finalTranscript;
            }}
            updateStats();
        }};

        rec.onerror = function(event) {{
            console.error("Speech Recognition Error:", event.error);
            document.getElementById('statusText').innerText = "Error: " + event.error;
            stopRecording();
        }};

        rec.onend = function() {{
            stopRecording();
        }};

        return rec;
    }}

    function toggleSpeechRecognition() {{
        if (!recognition) {{
            recognition = initSpeechRecognition();
        }}
        if (!recognition) return;

        if (isRecording) {{
            recognition.stop();
            stopRecording();
        }} else {{
            try {{
                recognition.start();
            }} catch(e) {{
                console.warn(e);
            }}
        }}
    }}

    function stopRecording() {{
        isRecording = false;
        document.getElementById('statusText').innerText = "Stopped";
        document.getElementById('statusDot').style.background = "#64748B";
        document.getElementById('toggleRecordBtn').innerText = "🎤 Start Speaking";
        document.getElementById('toggleRecordBtn').style.background = "#10B981";
        if (timerInterval) clearInterval(timerInterval);
    }}

    function updateStats() {{
        const txt = document.getElementById('liveTranscript').value.trim();
        const words = txt ? txt.split(/\\s+/).length : 0;
        let secs = 0;
        if (startTime && isRecording) {{
            secs = Math.floor((Date.now() - startTime) / 1000);
        }}
        document.getElementById('wordCounter').innerText = "Words: " + words + " | Duration: " + secs + "s";
    }}

    function clearTranscript() {{
        document.getElementById('liveTranscript').value = '';
        updateStats();
    }}

    function copyTranscript() {{
        const txtArea = document.getElementById('liveTranscript');
        txtArea.select();
        navigator.clipboard.writeText(txtArea.value);
        alert("Transcript copied to clipboard! Paste it into the response box.");
    }}
    </script>
    """
