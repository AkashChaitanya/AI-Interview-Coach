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
        session_results: list,
        overall_summary: dict
    ) -> str:
        """Generates a beautiful print-ready HTML report."""
        from datetime import datetime
        date_str = datetime.now().strftime("%B %d, %Y")
        
        avg_score = overall_summary.get("average_score", 0)
        avg_star = overall_summary.get("average_star", 0)
        avg_wpm = overall_summary.get("average_wpm", 0)
        total_fillers = overall_summary.get("total_fillers", 0)
        
        # Score color
        if avg_score >= 80: score_color = "#10B981"; rating = "Exceptional"
        elif avg_score >= 60: score_color = "#06B6D4"; rating = "Proficient"  
        elif avg_score >= 40: score_color = "#F59E0B"; rating = "Developing"
        else: score_color = "#EF4444"; rating = "Needs Work"
        
        # Build per-question sections
        q_sections = ""
        for i, item in enumerate(session_results, 1):
            q = item.get("question", {})
            ev = item.get("evaluation", {})
            ai = item.get("aiReply", {})
            score = round(ev.get("overall_score", 0))
            star = round(ev.get("star", {}).get("star_score", 0))
            wpm = ev.get("fluency", {}).get("estimated_wpm", 0)
            fillers = ev.get("fluency", {}).get("filler_count", 0)
            verdict = ai.get("validation_verdict", "Analyzed")
            feedback = ai.get("conversational_feedback", "")
            follow_up = ai.get("follow_up_question", "")
            exemplar = ai.get("model_exemplar_answer", "")
            
            # Verdict badge color
            verdict_colors = {
                "Strong / Correct": "#10B981",
                "Factually Incorrect": "#EF4444",
                "Creative / Unconventional": "#F59E0B",
                "Partially Correct": "#06B6D4",
                "Off-Topic / Vague": "#94A3B8"
            }
            v_color = verdict_colors.get(verdict, "#8B5CF6")
            
            # Score ring color
            s_color = "#10B981" if score >= 80 else "#06B6D4" if score >= 60 else "#F59E0B" if score >= 40 else "#EF4444"
            
            # STAR sentences
            tagged = ev.get("star", {}).get("tagged_sentences", [])
            star_html = ""
            tag_colors = {"Situation": "#8B5CF6", "Task": "#06B6D4", "Action": "#10B981", "Result": "#F59E0B"}
            for t in tagged:
                tc = tag_colors.get(t.get("tag",""), "#94A3B8")
                star_html += f'<div style="margin-bottom:4px"><span style="background:{tc}22;color:{tc};font-size:9px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;text-transform:uppercase">{t.get("tag","?")}</span><span style="font-size:12px;color:#374151">{t.get("sentence","")}</span></div>'
            
            q_sections += f"""
        <div style="page-break-inside:avoid;margin-bottom:32px;border:1px solid #E5E7EB;border-radius:12px;overflow:hidden">
          <!-- Q Header -->
          <div style="background:linear-gradient(135deg,#F8F9FF,#F0F4FF);padding:16px 20px;border-bottom:1px solid #E5E7EB;display:flex;align-items:center;justify-content:space-between">
            <div>
              <span style="font-size:10px;font-weight:700;color:#8B5CF6;text-transform:uppercase;letter-spacing:0.5px">Question {i} · {q.get("category","Technical")} · {q.get("difficulty","Mid")}</span>
              <p style="margin:4px 0 0;font-size:14px;font-weight:600;color:#111827;line-height:1.4">{q.get("question","")}</p>
            </div>
            <div style="text-align:center;min-width:60px">
              <div style="font-size:28px;font-weight:900;color:{s_color};font-family:monospace;line-height:1">{score}</div>
              <div style="font-size:9px;color:#6B7280;text-transform:uppercase">Score</div>
            </div>
          </div>
          
          <!-- AI Verdict -->
          <div style="padding:12px 20px;background:#FAFAFA;border-bottom:1px solid #F3F4F6;display:flex;align-items:center;gap:12px">
            <span style="background:{v_color}22;color:{v_color};font-size:10px;font-weight:700;padding:4px 10px;border-radius:20px;border:1px solid {v_color}44;text-transform:uppercase;white-space:nowrap">AI: {verdict}</span>
            <p style="margin:0;font-size:12px;color:#374151;line-height:1.5;font-style:italic">"{feedback}"</p>
          </div>
          
          <!-- Stats Row -->
          <div style="display:grid;grid-template-columns:repeat(3,1fr);padding:12px 20px;gap:12px;border-bottom:1px solid #F3F4F6">
            <div style="text-align:center"><div style="font-size:18px;font-weight:700;color:#06B6D4;font-family:monospace">{star}%</div><div style="font-size:9px;color:#9CA3AF;text-transform:uppercase">STAR Score</div></div>
            <div style="text-align:center"><div style="font-size:18px;font-weight:700;color:#8B5CF6;font-family:monospace">{wpm} WPM</div><div style="font-size:9px;color:#9CA3AF;text-transform:uppercase">Speaking Rate</div></div>
            <div style="text-align:center"><div style="font-size:18px;font-weight:700;color:#F59E0B;font-family:monospace">{fillers}</div><div style="font-size:9px;color:#9CA3AF;text-transform:uppercase">Filler Words</div></div>
          </div>
          
          <!-- STAR Breakdown -->
          {"<div style='padding:12px 20px;border-bottom:1px solid #F3F4F6'><div style='font-size:10px;font-weight:700;color:#374151;text-transform:uppercase;margin-bottom:8px'>STAR Sentence Classification</div>" + star_html + "</div>" if star_html else ""}
          
          <!-- Exemplar + Follow-up -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:0">
            {"<div style='padding:14px 20px;border-right:1px solid #F3F4F6'><div style='font-size:10px;font-weight:700;color:#F59E0B;text-transform:uppercase;margin-bottom:6px'>⭐ Model Exemplar Answer</div><p style='margin:0;font-size:11px;color:#374151;line-height:1.6'>" + exemplar + "</p></div>" if exemplar else ""}
            {"<div style='padding:14px 20px'><div style='font-size:10px;font-weight:700;color:#8B5CF6;text-transform:uppercase;margin-bottom:6px'>🔍 Interviewer Follow-up</div><p style='margin:0;font-size:11px;color:#374151;line-height:1.6;font-style:italic'>\"" + follow_up + "\"</p></div>" if follow_up else ""}
          </div>
        </div>
        """
        
        # Overall strengths / recommendations based on scores
        recommendations = []
        if avg_star < 60: recommendations.append("Practice structuring answers using the STAR framework (Situation, Task, Action, Result).")
        if total_fillers > 5: recommendations.append(f"Reduce verbal filler words ({total_fillers} detected). Practice deliberate pausing instead.")
        if avg_wpm > 180: recommendations.append("Speaking rate is high. Aim for 140-170 WPM for clarity and emphasis.")
        if avg_wpm < 100 and avg_wpm > 0: recommendations.append("Speaking pace is slow. Confidence-building practice can help increase fluency.")
        if avg_score >= 75: recommendations.append("Strong overall performance. Focus on quantifying business impact in behavioral answers.")
        if not recommendations: recommendations.append("Continue practicing with varied question types and domains to maintain sharpness.")
        
        recs_html = "".join(f'<li style="margin-bottom:6px;font-size:12px;color:#374151">{r}</li>' for r in recommendations)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Interview Assessment — {candidate_name}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: #FFFFFF; color: #111827; line-height: 1.6; }}
  @page {{ margin: 20mm; }}
  @media print {{ .no-print {{ display: none !important; }} body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
</style>
</head>
<body style="max-width:860px;margin:0 auto;padding:40px 32px">

  <!-- Header -->
  <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:32px;padding-bottom:24px;border-bottom:3px solid #8B5CF6">
    <div>
      <div style="font-size:11px;font-weight:700;color:#8B5CF6;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">AI Interview Coach Assessment</div>
      <h1 style="font-size:28px;font-weight:800;color:#111827;line-height:1.2">{candidate_name}</h1>
      <p style="font-size:13px;color:#6B7280;margin-top:4px">Interviewed by {persona_name.split("(")[0].strip()} · {date_str}</p>
    </div>
    <div style="text-align:right">
      <div style="font-size:48px;font-weight:900;color:{score_color};font-family:'JetBrains Mono',monospace;line-height:1">{avg_score}</div>
      <div style="font-size:11px;font-weight:700;color:{score_color};text-transform:uppercase">{rating}</div>
      <div style="font-size:10px;color:#9CA3AF">Overall Score / 100</div>
    </div>
  </div>

  <!-- Summary Metrics -->
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:32px">
    <div style="background:linear-gradient(135deg,#F0F9FF,#E0F2FE);border:1px solid #BAE6FD;border-radius:12px;padding:16px;text-align:center">
      <div style="font-size:24px;font-weight:800;color:#0284C7;font-family:monospace">{avg_star}%</div>
      <div style="font-size:10px;color:#0369A1;font-weight:600;text-transform:uppercase;margin-top:2px">STAR Adherence</div>
    </div>
    <div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border:1px solid #DDD6FE;border-radius:12px;padding:16px;text-align:center">
      <div style="font-size:24px;font-weight:800;color:#7C3AED;font-family:monospace">{avg_wpm}</div>
      <div style="font-size:10px;color:#6D28D9;font-weight:600;text-transform:uppercase;margin-top:2px">Avg WPM</div>
    </div>
    <div style="background:linear-gradient(135deg,#FFFBEB,#FEF3C7);border:1px solid #FDE68A;border-radius:12px;padding:16px;text-align:center">
      <div style="font-size:24px;font-weight:800;color:#D97706;font-family:monospace">{total_fillers}</div>
      <div style="font-size:10px;color:#B45309;font-weight:600;text-transform:uppercase;margin-top:2px">Filler Words</div>
    </div>
    <div style="background:linear-gradient(135deg,#F0FDF4,#DCFCE7);border:1px solid #BBF7D0;border-radius:12px;padding:16px;text-align:center">
      <div style="font-size:24px;font-weight:800;color:#16A34A;font-family:monospace">{len(session_results)}</div>
      <div style="font-size:10px;color:#15803D;font-weight:600;text-transform:uppercase;margin-top:2px">Questions Done</div>
    </div>
  </div>

  <!-- Recommendations -->
  <div style="margin-bottom:32px;background:#FAFAFA;border:1px solid #E5E7EB;border-radius:12px;padding:20px">
    <h3 style="font-size:13px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px">🎯 AI Coaching Recommendations</h3>
    <ul style="padding-left:20px;list-style:disc">{recs_html}</ul>
  </div>

  <!-- Per-Question Breakdown -->
  <h2 style="font-size:16px;font-weight:700;color:#111827;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid #E5E7EB">📋 Question-by-Question Breakdown</h2>
  {q_sections}

  <!-- Footer -->
  <div style="margin-top:40px;padding-top:16px;border-top:1px solid #E5E7EB;display:flex;justify-content:space-between;align-items:center">
    <span style="font-size:10px;color:#9CA3AF">AI Interview Coach · Computational Linguistics &amp; AI Platform · 100% Free &amp; Open Source</span>
    <span style="font-size:10px;color:#9CA3AF;font-family:monospace">Generated {date_str}</span>
  </div>

</body>
</html>"""

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
