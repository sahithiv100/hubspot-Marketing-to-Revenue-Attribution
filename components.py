"""
UI Components and Theme Styling for HubSpot Attribution Prototype.
Provides custom dark navy/charcoal styling with purple accents, KPI metric cards,
disclaimer banners, callout badges, and human-in-the-loop review notices.
"""

import streamlit as st

DARK_THEME_CSS = """
<style>
    /* Global styles */
    .stApp {
        background-color: #0E1117;
        color: #E2E8F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Top Synthetic Banner */
    .synthetic-banner {
        background: linear-gradient(90deg, #3B1C52 0%, #1E1B4B 100%);
        border: 1px solid #8B5CF6;
        border-radius: 8px;
        padding: 10px 18px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #F3E8FF;
        font-size: 0.88rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15);
    }
    .synthetic-pill {
        background-color: #7C3AED;
        color: #FFFFFF;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #161B26;
        border: 1px solid #283149;
        border-radius: 10px;
        padding: 16px 18px;
        transition: all 0.2s ease-in-out;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        border-color: #8B5CF6;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.12);
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #8B5CF6, #6366F1);
    }
    .kpi-label {
        color: #94A3B8;
        font-size: 0.80rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #F8FAFC;
        font-size: 1.70rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 0.78rem;
        color: #A78BFA;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .kpi-subtext.positive {
        color: #34D399;
    }
    .kpi-subtext.negative {
        color: #F87171;
    }

    /* Section Cards */
    .section-card {
        background-color: #161B26;
        border: 1px solid #232D42;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .section-title {
        color: #F8FAFC;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Manager Question Box */
    .manager-box {
        background: #181E30;
        border-left: 4px solid #8B5CF6;
        border-radius: 0 8px 8px 0;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .manager-title {
        color: #C4B5FD;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 6px;
    }
    .manager-answer {
        color: #E2E8F0;
        font-size: 0.90rem;
        line-height: 1.5;
    }

    /* Disclaimer & Governance Notice */
    .governance-notice {
        background-color: #1A1D2B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 16px 0;
        font-size: 0.83rem;
        color: #CBD5E1;
        line-height: 1.45;
    }
    .governance-tag {
        color: #F59E0B;
        font-weight: 700;
        margin-right: 6px;
    }

    /* Human Review Gate Badge */
    .human-review-badge {
        display: inline-block;
        background-color: #312E81;
        border: 1px solid #6366F1;
        color: #C7D2FE;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 8px;
    }
</style>
"""

def apply_custom_theme():
    """Injects custom CSS into the Streamlit application."""
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

def render_synthetic_banner():
    """Renders the top persistent synthetic data disclaimer."""
    st.markdown("""
    <div class="synthetic-banner">
        <div>
            <span>🧪 <strong>SYNTHETIC DEMO DATA — NOT REAL COMPANY DATA</strong> | HubSpot Marketing-to-Revenue Prototype</span>
        </div>
        <div>
            <span class="synthetic-pill">Fictional Simulation</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(label: str, value: str, subtext: str = "", trend: str = "neutral"):
    """
    Renders an individual styled KPI card.
    trend: 'positive', 'negative', or 'neutral'
    """
    trend_class = "positive" if trend == "positive" else ("negative" if trend == "negative" else "")
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-subtext {trend_class}">{subtext}</div>' if subtext else ''}
    </div>
    """

def render_manager_question(question_num: int, question: str, takeaway: str, details: str):
    """Renders an interactive manager question callout box."""
    st.markdown(f"""
    <div class="manager-box">
        <div class="manager-title">💡 Manager Question #{question_num}: {question}</div>
        <div class="manager-answer">
            <strong>Key Finding:</strong> {takeaway}<br>
            <span style="color: #94A3B8; font-size: 0.85rem;">{details}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_causal_disclaimer():
    """Renders the standard attribution vs causality disclosure."""
    st.markdown("""
    <div class="governance-notice">
        <span class="governance-tag">⚠️ METHODOLOGY DISCLOSURE:</span>
        <strong>Attribution vs. Causal Proof:</strong> First-touch, last-touch, linear, and U-shaped models
        are heuristic accounting frameworks that distribute credit along observed consumer journeys. They
        measure correlation, not counterfactual incrementality. High-impact budget reallocations or channel eliminations
        must be validated via controlled geo-holdout or conversion lift experiments with human executive review.
    </div>
    """, unsafe_allow_html=True)
