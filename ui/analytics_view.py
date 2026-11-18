"""
Linguistic Analytics & Visualization Dashboard for AI Interview Coach.
Builds interactive Plotly charts, radar charts, and report download triggers.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
from core.report_generator import ReportGenerator

report_gen = ReportGenerator()

def render_radar_chart(metrics: Dict[str, float]):
    """Renders available observed metrics without filling unavailable axes."""
    categories = [
        "Answer relevance",
        "STAR structure",
        "Fluency markers",
        "Communication clarity",
        "Speaking pace"
    ]
    values = [
        metrics.get("relevance"),
        metrics.get("star"),
        metrics.get("fluency"),
        metrics.get("clarity"),
        metrics.get("pace")
    ]
    # Close the loop
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(96, 165, 250, 0.25)',
        line=dict(color='#60A5FA', width=2.5),
        name='Candidate Profile'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color="#94A3B8"),
                gridcolor="rgba(255, 255, 255, 0.1)"
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#E2E8F0"),
                linecolor="rgba(255, 255, 255, 0.1)"
            ),
            bgcolor="rgba(15, 23, 42, 0.5)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=30, b=30),
        showlegend=False,
        height=320
    )
    st.plotly_chart(fig, use_container_width=True)


def render_filler_chart(filler_breakdown: Dict[str, int]):
    """Renders horizontal bar chart of detected verbal fillers."""
    if not filler_breakdown:
        st.info("No verbal filler words detected across recorded responses!")
        return

    words = list(filler_breakdown.keys())
    counts = list(filler_breakdown.values())

    fig = go.Figure(go.Bar(
        x=counts,
        y=words,
        orientation='h',
        marker=dict(
            color='#F87171',
            line=dict(color='rgba(255,255,255,0.2)', width=1)
        )
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Occurrences", color="#94A3B8", gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(color="#E2E8F0"),
        margin=dict(l=20, r=20, t=20, b=20),
        height=220
    )
    st.plotly_chart(fig, use_container_width=True)


def render_performance_history_chart(scores: List[float]):
    """Renders line chart showing question-by-question score progression."""
    if len(scores) < 2:
        return

    labels = [f"Q{i+1}" for i in range(len(scores))]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels,
        y=scores,
        mode='lines+markers',
        line=dict(color='#34D399', width=3),
        marker=dict(size=8, color='#10B981')
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(color="#94A3B8", gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(title="Score (0-100)", range=[0, 105], color="#94A3B8", gridcolor="rgba(255,255,255,0.08)"),
        margin=dict(l=20, r=20, t=20, b=20),
        height=220
    )
    st.plotly_chart(fig, use_container_width=True)


def render_session_analytics_dashboard(session_history: List[Dict[str, Any]], candidate_name: str, persona_name: str):
    """Renders the full analytics view for completed or ongoing interview sessions."""
    if not session_history:
        st.info("No interview questions answered yet. Start a session in the 'Live Interview Studio' tab to view linguistic analytics!")
        return

    # Calculate aggregations
    scores = [
        item["evaluation"]["overall_score"] for item in session_history
        if isinstance(item["evaluation"].get("overall_score"), (int, float))
    ]
    star_scores = [
        item["evaluation"]["score_components"]["star_structure"]
        for item in session_history
        if "star_structure" in item["evaluation"].get("score_components", {})
    ]
    wpms = [
        item["evaluation"]["fluency"]["estimated_wpm"] for item in session_history
        if isinstance(item["evaluation"]["fluency"].get("estimated_wpm"), (int, float))
    ]
    total_fillers = sum(item["evaluation"]["fluency"]["filler_count"] for item in session_history)

    # Combined filler breakdown
    aggregated_fillers = {}
    for item in session_history:
        fb = item["evaluation"]["fluency"].get("filler_breakdown", {})
        for word, cnt in fb.items():
            aggregated_fillers[word] = aggregated_fillers.get(word, 0) + cnt

    avg_score = sum(scores) / len(scores) if scores else None
    avg_star = sum(star_scores) / len(star_scores) if star_scores else None
    avg_wpm = sum(wpms) / len(wpms) if wpms else None
    average_metric = lambda key: (
        sum(item["evaluation"].get(key, 0) for item in session_history) / len(session_history)
        if session_history else None
    )
    relevance_values = [
        item["evaluation"]["score_components"]["answer_relevance"]
        for item in session_history
        if "answer_relevance" in item["evaluation"].get("score_components", {})
    ]
    fluency_values = [
        item["evaluation"]["fluency"]["fluency_score"] for item in session_history
    ]
    pace_score = None if avg_wpm is None else (
        max(0.0, 100.0 - (120.0 - avg_wpm) * 0.25) if avg_wpm < 120 else
        max(0.0, 100.0 - (avg_wpm - 165.0) * 0.25) if avg_wpm > 165 else 100.0
    )

    # Summary metrics cards
    st.markdown("### 📈 Comprehensive Linguistic Performance Scorecard")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Overall Score", f"{avg_score:.1f} / 100" if avg_score is not None else "Not scored")
    with col2:
        st.metric("Avg STAR Adherence", f"{avg_star:.1f}%" if avg_star is not None else "N/A")
    with col3:
        st.metric("Avg Speech Pace", f"{avg_wpm:.1f} WPM" if avg_wpm is not None else "Not measured")
    with col4:
        st.metric("Total Filler Words", f"{total_fillers}")

    st.markdown("---")

    # Chart columns
    c_left, c_right = st.columns([1, 1])
    with c_left:
        st.markdown("#### 🎯 5-Axis Competency Radar")
        radar_metrics = {
            "relevance": sum(relevance_values) / len(relevance_values) if relevance_values else None,
            "star": avg_star,
            "fluency": sum(fluency_values) / len(fluency_values) if fluency_values else None,
            "clarity": average_metric("communication_clarity_score"),
            "pace": pace_score
        }
        render_radar_chart(radar_metrics)

    with c_right:
        st.markdown("#### 🗣️ Filler Word Frequency")
        render_filler_chart(aggregated_fillers)

    if len(scores) >= 2:
        st.markdown("#### 📉 Score Trajectory Across Questions")
        render_performance_history_chart(scores)

    st.markdown("---")
    st.markdown("### 📥 Export Official Assessment Report")

    summary_data = {
        "average_score": avg_score,
        "average_star": avg_star,
        "average_wpm": avg_wpm,
        "total_fillers": total_fillers,
        "total_questions_answered": len(session_history)
    }

    md_report = report_gen.generate_markdown_report(candidate_name, persona_name, session_history, summary_data)
    json_report = report_gen.generate_json_export(candidate_name, persona_name, session_history, summary_data)

    c_dl1, c_dl2 = st.columns(2)
    with c_dl1:
        st.download_button(
            label="📄 Download Markdown Report (.md)",
            data=md_report,
            file_name=f"Interview_Report_{candidate_name.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with c_dl2:
        st.download_button(
            label="📊 Download JSON Analytics (.json)",
            data=json_report,
            file_name=f"Interview_Analytics_{candidate_name.replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
