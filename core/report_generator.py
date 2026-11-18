"""
Interview Assessment Report Generator.
Aggregates session analytics and exports comprehensive Markdown, JSON, and summary scorecards.
"""

import json
from datetime import datetime
from typing import Dict, List, Any

class ReportGenerator:
    def __init__(self):
        pass

    def generate_markdown_report(
        self,
        candidate_name: str,
        persona_name: str,
        session_results: List[Dict[str, Any]],
        overall_summary: Dict[str, Any]
    ) -> str:
        """Generates a downloadable GitHub-flavored Markdown assessment report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        avg_score = overall_summary.get("average_score")
        avg_star = overall_summary.get("average_star")
        avg_wpm = overall_summary.get("average_wpm")
        total_fillers = overall_summary.get("total_fillers", 0)
        score_text = f"{avg_score:.1f} / 100" if isinstance(avg_score, (int, float)) else "Not scored"
        star_text = f"{avg_star:.1f}" if isinstance(avg_star, (int, float)) else "N/A"
        wpm_text = f"{avg_wpm:.1f} WPM" if isinstance(avg_wpm, (int, float)) else "Not measured"
        readiness = (
            "🌟 Exceptional" if avg_score >= 85 else "✅ Strong" if avg_score >= 70
            else "⚠️ Needs Refinement"
        ) if isinstance(avg_score, (int, float)) else "Not scored"

        report = f"""# 🎙️ AI Interview Coach Assessment Report
**Candidate Name:** {candidate_name}  
**Date & Time:** {timestamp}  
**Interviewer Persona:** {persona_name}  
**Overall Performance Score:** **{score_text}**

---

## 📊 Executive Summary & Core Competencies

| Competency Area | Score (0-100) | Benchmark Rating |
| :--- | :--- | :--- |
| **Overall Readiness** | **{score_text}** | {readiness} |
| **STAR Framework Structure** | **{star_text}** | {"N/A" if avg_star is None else "Measured on behavioral answers only"} |
| **Speaking Rate & Pacing** | **{wpm_text}** | {"Measured only when response duration is supplied" if avg_wpm is not None else "Not measured (no audio duration supplied)"} |
| **Verbal Filler Count** | **{total_fillers} total** | {"🌟 Extremely Polished" if total_fillers <= 3 else "✅ Acceptable" if total_fillers <= 8 else "⚠️ High Verbal Hesitation"} |

---

## 📝 Detailed Question-by-Question Transcript & Coaching

"""
        for idx, item in enumerate(session_results, start=1):
            q_info = item.get("question", {})
            eval_info = item.get("evaluation", {})
            ans_text = item.get("answer", "No answer recorded.")
            ai_reply = item.get("ai_reply", item.get("aiReply", ""))
            if isinstance(ai_reply, dict):
                ai_reply = ai_reply.get("conversational_feedback", "")
            score = eval_info.get("overall_score")
            star = eval_info.get("star", {})
            fluency = eval_info.get("fluency", {})
            tone = eval_info.get("tone", {})
            score_label = (
                f"{score:.1f} / 100" if isinstance(score, (int, float))
                else "Not scored (follow-up has no independent rubric)"
            )
            wpm_value = fluency.get("estimated_wpm")
            wpm_label = f"{wpm_value} WPM" if isinstance(wpm_value, (int, float)) else "Not measured"

            report += f"""### Question {idx}: {q_info.get('category', 'Technical')} ({q_info.get('difficulty', 'Mid')})
> **Prompt:** *"{q_info.get('question', '')}"*

**Your Answer:**
> {ans_text}

**Interviewer Response:**
> *"{ai_reply}"*

**Evaluation Metrics:**
- **Overall Answer Score:** **{score_label}**
- **STAR Structure:** Situation: {'✅' if star.get('coverage', {}).get('Situation') else '❌'} | Task: {'✅' if star.get('coverage', {}).get('Task') else '❌'} | Action: {'✅' if star.get('coverage', {}).get('Action') else '❌'} | Result: {'✅' if star.get('coverage', {}).get('Result') else '❌'}
- **Text Metrics:** {fluency.get('word_count', 0)} words, {fluency.get('filler_count', 0)} filler markers, {wpm_label} ({fluency.get('tempo_status', '')})
- **Communication markers:** {tone.get('tone_label', 'Not analyzed')} (text-only language indicators; not a psychological assessment)

**Coaching Tips:**
"""
            for tip in eval_info.get("coaching_summary", []):
                report += f"- {tip}\n"

            report += "\n---\n\n"

        report += """## 🚀 Recommended Next Steps for Interview Preparation
1. **Refine Quantifiable STAR Results**: Ensure every project story ends with concrete numbers (% latency reduction, dollars saved, user engagement increase).
2. **Master Natural Pauses**: Replace verbal fillers (*um*, *uh*, *like*) with deliberate silent pauses to project authority.
3. **Practice Technical Deep Dives**: Regularly rehearse architectural trade-offs, edge cases, and failure modes.

*Generated automatically by AI Interview Coach (Computational Linguistics & AI Project).*
"""
        return report

    def generate_json_export(
        self,
        candidate_name: str,
        persona_name: str,
        session_results: List[Dict[str, Any]],
        overall_summary: Dict[str, Any]
    ) -> str:
        data = {
            "metadata": {
                "candidate_name": candidate_name,
                "persona": persona_name,
                "timestamp": datetime.now().isoformat(),
                "engine": "AI-Interview-Coach v2.0"
            },
            "summary": overall_summary,
            "session_results": session_results
        }
        return json.dumps(data, indent=2)

    def generate_html_report(
        self,
        candidate_name: str,
        persona_name: str,
        session_results: List[Dict[str, Any]],
        overall_summary: Dict[str, Any]
    ) -> str:
        """Generates a beautiful, print-ready HTML report with per-question breakdowns."""
        timestamp = datetime.now().strftime("%B %d, %Y at %H:%M")
        avg_score = overall_summary.get("average_score")
        avg_star = overall_summary.get("average_star")
        avg_wpm = overall_summary.get("average_wpm")
        total_fillers = overall_summary.get("total_fillers", 0)

        score_text = f"{avg_score:.1f}" if isinstance(avg_score, (int, float)) else "N/A"
        star_text = f"{avg_star:.1f}" if isinstance(avg_star, (int, float)) else "N/A"
        wpm_text = f"{avg_wpm:.0f}" if isinstance(avg_wpm, (int, float)) else "N/A"

        if isinstance(avg_score, (int, float)):
            if avg_score >= 85:
                readiness = "🌟 Exceptional"
                readiness_color = "#22c55e"
            elif avg_score >= 70:
                readiness = "✅ Strong"
                readiness_color = "#3b82f6"
            else:
                readiness = "⚠️ Needs Refinement"
                readiness_color = "#f59e0b"
        else:
            readiness = "Not scored"
            readiness_color = "#6b7280"

        def verdict_badge(verdict: str) -> str:
            colors = {
                "Strong / Correct": ("#dcfce7", "#166534"),
                "Partially Correct": ("#fef9c3", "#854d0e"),
                "Factually Incorrect": ("#fee2e2", "#991b1b"),
                "Creative / Unconventional": ("#ede9fe", "#5b21b6"),
                "Off-Topic / Vague": ("#f3f4f6", "#374151"),
            }
            bg, fg = colors.get(verdict, ("#f3f4f6", "#374151"))
            return (
                f'<span style="background:{bg};color:{fg};padding:3px 10px;'
                f'border-radius:12px;font-size:0.78rem;font-weight:600;">{verdict}</span>'
            )

        def star_check(val: bool) -> str:
            return "✅" if val else "❌"

        # Build per-question HTML
        questions_html = ""
        for idx, item in enumerate(session_results, start=1):
            q_info = item.get("question", {})
            eval_info = item.get("evaluation", {})
            ans_text = item.get("answer", "No answer recorded.")
            ai_reply = item.get("ai_reply", item.get("aiReply", ""))
            if isinstance(ai_reply, dict):
                verdict_str = ai_reply.get("validation_verdict", "")
                feedback_str = ai_reply.get("conversational_feedback", "")
                follow_up_str = ai_reply.get("follow_up_question", "")
                exemplar_str = ai_reply.get("model_exemplar_answer", "")
            else:
                verdict_str = ""
                feedback_str = str(ai_reply)
                follow_up_str = ""
                exemplar_str = ""

            score = eval_info.get("overall_score")
            star = eval_info.get("star", {})
            fluency = eval_info.get("fluency", {})
            tone = eval_info.get("tone", {})
            coaching = eval_info.get("coaching_summary", [])
            score_label = f"{score:.1f} / 100" if isinstance(score, (int, float)) else "Not scored"
            wpm_val = fluency.get("estimated_wpm")
            wpm_label = f"{wpm_val} WPM" if isinstance(wpm_val, (int, float)) else "Not measured"
            star_cov = star.get("coverage", {})

            questions_html += f"""
        <div class="q-card">
          <div class="q-header">
            <span class="q-num">Q{idx}</span>
            <span class="q-meta">{q_info.get('category','Technical')} &bull; {q_info.get('difficulty','Mid')}</span>
            {verdict_badge(verdict_str) if verdict_str else ''}
          </div>
          <p class="q-prompt">❝ {q_info.get('question','')} ❞</p>

          <div class="section-label">Candidate Answer</div>
          <div class="answer-box">{ans_text}</div>

          <div class="metrics-grid">
            <div class="metric-box">
              <div class="metric-title">Score</div>
              <div class="metric-value">{score_label}</div>
            </div>
            <div class="metric-box">
              <div class="metric-title">Words / WPM</div>
              <div class="metric-value">{fluency.get('word_count',0)} / {wpm_label}</div>
            </div>
            <div class="metric-box">
              <div class="metric-title">Filler Words</div>
              <div class="metric-value">{fluency.get('filler_count',0)}</div>
            </div>
            <div class="metric-box">
              <div class="metric-title">Tone</div>
              <div class="metric-value">{tone.get('tone_label','N/A')}</div>
            </div>
          </div>

          <div class="star-row">
            <span class="star-label">STAR:</span>
            <span>Situation {star_check(star_cov.get('Situation',False))}</span>
            <span>Task {star_check(star_cov.get('Task',False))}</span>
            <span>Action {star_check(star_cov.get('Action',False))}</span>
            <span>Result {star_check(star_cov.get('Result',False))}</span>
          </div>

          {f'<div class="section-label">AI Feedback</div><div class="feedback-box">{feedback_str}</div>' if feedback_str else ''}
          {f'<div class="section-label">Follow-up Question</div><div class="followup-box">{follow_up_str}</div>' if follow_up_str else ''}
          {f'<div class="section-label">Model Exemplar Answer</div><div class="exemplar-box">{exemplar_str}</div>' if exemplar_str else ''}

          {"".join(f'<div class="tip">💡 {tip}</div>' for tip in coaching) if coaching else ''}
        </div>
"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Interview Report — {candidate_name}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', system-ui, sans-serif;
    background: #f8fafc;
    color: #1e293b;
    padding: 32px 16px;
  }}
  .report-wrap {{ max-width: 860px; margin: 0 auto; }}

  /* Header */
  .report-header {{
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    color: #fff;
    border-radius: 16px;
    padding: 36px 40px;
    margin-bottom: 28px;
  }}
  .report-header h1 {{ font-size: 1.7rem; font-weight: 700; margin-bottom: 6px; }}
  .report-header .sub {{ color: #94a3b8; font-size: 0.9rem; }}
  .report-header .meta {{ margin-top: 18px; display: flex; gap: 32px; flex-wrap: wrap; }}
  .report-header .meta-item {{ }}
  .report-header .meta-label {{ font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing:.05em; }}
  .report-header .meta-value {{ font-size: 1rem; font-weight: 600; color: #e2e8f0; }}

  /* Summary */
  .summary-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 16px;
    margin-bottom: 28px;
  }}
  .summary-card {{
    background: #fff;
    border-radius: 12px;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,.07);
    border-top: 4px solid #6366f1;
  }}
  .summary-card .s-label {{ font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing:.05em; margin-bottom: 6px; }}
  .summary-card .s-value {{ font-size: 1.5rem; font-weight: 700; color: #1e293b; }}
  .summary-card .s-sub {{ font-size: 0.75rem; color: #94a3b8; margin-top: 2px; }}

  /* Section heading */
  .section-heading {{
    font-size: 1.1rem; font-weight: 700; color: #1e293b;
    margin: 32px 0 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
  }}

  /* Q Card */
  .q-card {{
    background: #fff;
    border-radius: 12px;
    padding: 24px 26px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,.07);
  }}
  .q-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }}
  .q-num {{
    background: #6366f1; color: #fff;
    border-radius: 8px; padding: 3px 10px;
    font-size: 0.8rem; font-weight: 700;
  }}
  .q-meta {{ color: #64748b; font-size: 0.8rem; }}
  .q-prompt {{
    font-style: italic; color: #374151;
    background: #f1f5f9; border-left: 3px solid #6366f1;
    padding: 10px 14px; border-radius: 6px; margin-bottom: 14px;
    font-size: 0.93rem;
  }}

  /* Answer box */
  .section-label {{ font-size: 0.72rem; font-weight: 600; color: #6366f1; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 5px; }}
  .answer-box {{
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 12px 14px;
    font-size: 0.88rem; color: #374151; margin-bottom: 14px;
    white-space: pre-wrap; word-break: break-word;
  }}

  /* Metrics */
  .metrics-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 10px; margin-bottom: 14px;
  }}
  .metric-box {{
    background: #f1f5f9; border-radius: 8px; padding: 10px 12px;
  }}
  .metric-title {{ font-size: 0.68rem; color: #64748b; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 3px; }}
  .metric-value {{ font-size: 0.92rem; font-weight: 600; color: #1e293b; }}

  /* STAR */
  .star-row {{
    display: flex; gap: 14px; align-items: center;
    font-size: 0.82rem; color: #374151;
    background: #f8fafc; border-radius: 8px; padding: 8px 12px;
    margin-bottom: 14px; flex-wrap: wrap;
  }}
  .star-label {{ font-weight: 700; color: #6366f1; }}

  /* Feedback */
  .feedback-box {{
    background: #eff6ff; border-left: 3px solid #3b82f6;
    border-radius: 6px; padding: 10px 14px;
    font-size: 0.88rem; color: #1e3a5f; margin-bottom: 10px;
  }}
  .followup-box {{
    background: #fdf4ff; border-left: 3px solid #a855f7;
    border-radius: 6px; padding: 10px 14px;
    font-size: 0.88rem; color: #3b0764; margin-bottom: 10px;
  }}
  .exemplar-box {{
    background: #f0fdf4; border-left: 3px solid #22c55e;
    border-radius: 6px; padding: 10px 14px;
    font-size: 0.88rem; color: #14532d; margin-bottom: 10px;
    white-space: pre-wrap;
  }}
  .tip {{
    background: #fefce8; border-left: 3px solid #eab308;
    border-radius: 6px; padding: 7px 12px;
    font-size: 0.83rem; color: #713f12; margin-bottom: 6px;
  }}

  /* Recommendations */
  .rec-card {{
    background: #fff; border-radius: 12px;
    padding: 24px 26px; margin-top: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,.07);
  }}
  .rec-card ol {{ padding-left: 20px; }}
  .rec-card li {{ margin-bottom: 10px; font-size: 0.9rem; color: #374151; }}

  /* Footer */
  .report-footer {{
    text-align: center; color: #94a3b8; font-size: 0.75rem; margin-top: 40px;
  }}

  /* Print */
  @media print {{
    body {{ background: #fff; padding: 0; }}
    .report-header {{ background: #1e293b !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .q-card, .summary-card, .rec-card {{ box-shadow: none; border: 1px solid #e2e8f0; }}
  }}
</style>
</head>
<body>
<div class="report-wrap">

  <div class="report-header">
    <h1>🎙️ AI Interview Coach Assessment Report</h1>
    <div class="sub">Generated on {timestamp}</div>
    <div class="meta">
      <div class="meta-item">
        <div class="meta-label">Candidate</div>
        <div class="meta-value">{candidate_name}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Interviewer Persona</div>
        <div class="meta-value">{persona_name}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Overall Readiness</div>
        <div class="meta-value" style="color:{readiness_color};">{readiness}</div>
      </div>
    </div>
  </div>

  <div class="summary-grid">
    <div class="summary-card" style="border-top-color:#6366f1;">
      <div class="s-label">Overall Score</div>
      <div class="s-value">{score_text}</div>
      <div class="s-sub">out of 100</div>
    </div>
    <div class="summary-card" style="border-top-color:#3b82f6;">
      <div class="s-label">STAR Score</div>
      <div class="s-value">{star_text}</div>
      <div class="s-sub">framework coverage</div>
    </div>
    <div class="summary-card" style="border-top-color:#22c55e;">
      <div class="s-label">Speaking Rate</div>
      <div class="s-value">{wpm_text}</div>
      <div class="s-sub">words per minute</div>
    </div>
    <div class="summary-card" style="border-top-color:#f59e0b;">
      <div class="s-label">Total Fillers</div>
      <div class="s-value">{total_fillers}</div>
      <div class="s-sub">{"🌟 Polished" if total_fillers <= 3 else "✅ Acceptable" if total_fillers <= 8 else "⚠️ High"}</div>
    </div>
  </div>

  <div class="section-heading">📝 Question-by-Question Breakdown</div>
  {questions_html}

  <div class="rec-card">
    <div class="section-heading" style="margin-top:0;">🚀 Recommended Next Steps</div>
    <ol>
      <li><strong>Refine Quantifiable STAR Results</strong> — End every project story with concrete numbers (% latency reduction, dollars saved, user growth).</li>
      <li><strong>Master Natural Pauses</strong> — Replace verbal fillers (<em>um</em>, <em>uh</em>, <em>like</em>) with deliberate silent pauses to project authority.</li>
      <li><strong>Practice Technical Deep Dives</strong> — Regularly rehearse architectural trade-offs, edge cases, and failure modes under time pressure.</li>
    </ol>
  </div>

  <div class="report-footer">
    Generated automatically by AI Interview Coach (Computational Linguistics &amp; AI Project) &bull; {timestamp}
  </div>
</div>
</body>
</html>"""
        return html
