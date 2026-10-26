"""
Custom CSS styling and design system for AI Interview Coach.
"""

def get_custom_css() -> str:
    return """
    <style>
    /* Main container and font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Glassmorphic header card */
    .hero-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 12px;
    }

    .tag-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
        background: rgba(99, 102, 241, 0.15);
        color: #818CF8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    /* Interviewer Avatar Card */
    .interviewer-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 18px;
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 16px;
    }

    .interviewer-avatar {
        font-size: 3rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 50%;
        width: 64px;
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #60A5FA;
    }

    .interviewer-info h3 {
        margin: 0 0 4px 0;
        color: #F8FAFC;
        font-size: 1.2rem;
    }

    .interviewer-info p {
        margin: 0;
        color: #94A3B8;
        font-size: 0.9rem;
    }

    /* Metric Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
        margin: 16px 0;
    }

    .metric-tile {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .metric-tile:hover {
        transform: translateY(-2px);
        border-color: #60A5FA;
    }

    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 4px 0;
    }

    .metric-label {
        font-size: 0.78rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* STAR badge pills */
    .star-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px 4px 4px 0;
    }

    .star-present {
        background: rgba(34, 197, 94, 0.15);
        color: #4ADE80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }

    .star-missing {
        background: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* Waveform animation */
    .waveform-bar {
        display: inline-block;
        width: 4px;
        height: 18px;
        margin: 0 2px;
        background: #60A5FA;
        border-radius: 2px;
        animation: wave 1s ease-in-out infinite;
    }

    @keyframes wave {
        0%, 100% { height: 6px; }
        50% { height: 22px; }
    }

    /* Coaching tip box */
    .tip-box {
        background: rgba(59, 130, 246, 0.08);
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
        color: #E2E8F0;
        font-size: 0.95rem;
    }
    </style>
    """
