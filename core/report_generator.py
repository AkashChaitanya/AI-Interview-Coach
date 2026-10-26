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

        avg_score = overall_summary.get("average_score", 0.0)
        avg_star = overall_summary.get("average_star", 0.0)
        avg_wpm = overall_summary.get("average_wpm", 0.0)
        total_fillers = overall_summary.get("total_fillers", 0)

        report = f"""# 🎙️ AI Interview Coach Assessment Report
**Candidate Name:** {candidate_name}  
**Date & Time:** {timestamp}  
**Interviewer Persona:** {persona_name}  
**Overall Performance Score:** **{avg_score:.1f} / 100**  

---

## 📊 Executive Summary & Core Competencies

| Competency Area | Score (0-100) | Benchmark Rating |
| :--- | :--- | :--- |
| **Overall Readiness** | **{avg_score:.1f}** | {"🌟 Exceptional" if avg_score >= 85 else "✅ Strong" if avg_score >= 70 else "⚠️ Needs Refinement"} |
| **STAR Framework Structure** | **{avg_star:.1f}** | {"🌟 Comprehensive" if avg_star >= 80 else "✅ Good" if avg_star >= 60 else "⚠️ Missing Components"} |
| **Speaking Rate & Pacing** | **{avg_wpm:.1f} WPM** | {"✅ Optimal (120-165)" if 120 <= avg_wpm <= 165 else "⚠️ Fast (>165)" if avg_wpm > 165 else "⚠️ Slow (<120)"} |
| **Verbal Filler Count** | **{total_fillers} total** | {"🌟 Extremely Polished" if total_fillers <= 3 else "✅ Acceptable" if total_fillers <= 8 else "⚠️ High Verbal Hesitation"} |

---

## 📝 Detailed Question-by-Question Transcript & Coaching

"""
        for idx, item in enumerate(session_results, start=1):
            q_info = item.get("question", {})
            eval_info = item.get("evaluation", {})
            ans_text = item.get("answer", "No answer recorded.")
            ai_reply = item.get("ai_reply", "")
            score = eval_info.get("overall_score", 0.0)
            star = eval_info.get("star", {})
            fluency = eval_info.get("fluency", {})
            tone = eval_info.get("tone", {})

            report += f"""### Question {idx}: {q_info.get('category', 'Technical')} ({q_info.get('difficulty', 'Mid')})
> **Prompt:** *"{q_info.get('question', '')}"*

**Your Answer:**
> {ans_text}

**Interviewer Response:**
> *"{ai_reply}"*

**Evaluation Metrics:**
- **Overall Answer Score:** **{score:.1f} / 100**
- **STAR Structure:** Situation: {'✅' if star.get('coverage', {}).get('Situation') else '❌'} | Task: {'✅' if star.get('coverage', {}).get('Task') else '❌'} | Action: {'✅' if star.get('coverage', {}).get('Action') else '❌'} | Result: {'✅' if star.get('coverage', {}).get('Result') else '❌'}
- **Speech Metrics:** {fluency.get('word_count', 0)} words, {fluency.get('filler_count', 0)} fillers, {fluency.get('estimated_wpm', 0)} WPM ({fluency.get('tempo_status', '')})
- **Tone & Sentiment:** {tone.get('tone_label', 'Neutral')} ({tone.get('confidence_score', 0)}% confidence index)

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
