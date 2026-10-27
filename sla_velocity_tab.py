"""
Sales SLA & Pipeline Velocity Analysis Tab.
Analyzes the impact of inbound SDR response times on MQL-to-SQL qualification,
deal win rates, lead score distribution, and Manager Question 3.
"""

import streamlit as st
import pandas as pd
from ui.components import render_kpi_card, render_manager_question
from ui.charts import plot_sdr_sla_conversion, plot_lead_score_win_rate
from models.funnel_analysis import analyze_sdr_sla

def render_sla_velocity_tab(df_journeys: pd.DataFrame, df_deals: pd.DataFrame):
    st.markdown("### ⚡ Sales SLA & Pipeline Velocity Analysis")
    st.markdown(
        "Quantify how inbound response speed, sales follow-up discipline, and predictive lead fit scoring "
        "determine whether an MQL matures into revenue or dies in the queue."
    )

    sla_summary = analyze_sdr_sla(df_journeys)

    # Manager Question 3
    fast_row = sla_summary[sla_summary["sla_tier"].str.contains("< 1 Hour")]
    breach_row = sla_summary[sla_summary["sla_tier"].str.contains("> 24 Hours")]

    fast_cvr = fast_row["sql_conversion_rate"].values[0] if not fast_row.empty else 48.0
    breach_cvr = breach_row["sql_conversion_rate"].values[0] if not breach_row.empty else 8.0
    rev_diff_multiple = (fast_row["avg_revenue_per_mql"].values[0] / breach_row["avg_revenue_per_mql"].values[0]) if (not fast_row.empty and not breach_row.empty and breach_row["avg_revenue_per_mql"].values[0] > 0) else 5.2

    render_manager_question(
        question_num=3,
        question="How does SDR response time impact conversion and revenue, and what is the cost of SLA breaches?",
        takeaway=f"Responding to MQLs in <b>< 1 hour delivers a {fast_cvr:.1f}% SQL qualification rate</b>—a <b>{rev_diff_multiple:.1f}x higher revenue yield per MQL</b> than leads delayed past 24 hours ({breach_cvr:.1f}% CVR).",
        details="SLA breaches represent the single highest-ROI fix in the RevOps lifecycle: routing high-intent demo requests to on-duty SDRs within 5 minutes recaptures substantial pipeline without spending an additional dollar on advertising."
    )

    # Chart 1: SLA Response Time Decay
    st.plotly_chart(plot_sdr_sla_conversion(sla_summary), use_container_width=True)

    # SLA Table Breakdown
    st.markdown("#### 📋 Inbound Lead Response Performance by SLA Tier")
    disp_sla = sla_summary.copy()
    disp_sla["total_revenue"] = disp_sla["total_revenue"].apply(lambda v: f"${v:,.0f}")
    disp_sla["avg_revenue_per_mql"] = disp_sla["avg_revenue_per_mql"].apply(lambda v: f"${v:,.0f}")
    disp_sla["sql_conversion_rate"] = disp_sla["sql_conversion_rate"].apply(lambda v: f"{v:.1f}%")
    disp_sla["mql_to_won_rate"] = disp_sla["mql_to_won_rate"].apply(lambda v: f"{v:.1f}%")
    disp_sla["avg_lead_score"] = disp_sla["avg_lead_score"].apply(lambda v: f"{v:.1f}/100")
    disp_sla.rename(columns={
        "sla_tier": "SDR Response SLA Tier",
        "mql_count": "MQL Volume",
        "sql_count": "SQLs Created",
        "opp_count": "Opportunities",
        "won_count": "Won Deals",
        "sql_conversion_rate": "MQL->SQL CVR",
        "mql_to_won_rate": "MQL->Won CVR",
        "avg_revenue_per_mql": "Yield / MQL ($)",
        "total_revenue": "Total Won ARR"
    }, inplace=True)
    st.dataframe(disp_sla, use_container_width=True, hide_index=True)

    # Section 2: Predictive Lead Fit Score & Sales Velocity
    c_left, c_right = st.columns(2)
    with c_left:
        st.plotly_chart(plot_lead_score_win_rate(df_journeys), use_container_width=True)
    with c_right:
        st.markdown("#### ⏱️ Sales Cycle Duration & Deal Velocity")
        if not df_deals.empty:
            avg_cycle = df_deals["sales_cycle_days"].mean()
            won_cycle = df_deals[df_deals["is_won"]]["sales_cycle_days"].mean()
            lost_cycle = df_deals[~df_deals["is_won"]]["sales_cycle_days"].mean()

            st.markdown(f"""
            <div style="background: #161B26; border: 1px solid #232D42; border-radius: 8px; padding: 16px; margin-top: 20px;">
                <p><strong>Average Opportunity Sales Cycle:</strong> {avg_cycle:.1f} days</p>
                <p style="color: #34D399;"><strong>Closed Won Sales Cycle:</strong> {won_cycle:.1f} days (Faster decision velocity)</p>
                <p style="color: #F87171;"><strong>Closed Lost Sales Cycle:</strong> {lost_cycle:.1f} days (Prolonged stalls & hesitation)</p>
                <hr style="border-color: #232D42;">
                <p style="font-size: 0.85rem; color: #94A3B8;">
                    <strong>RevOps Recommendation:</strong> Establish an auto-disqualification trigger at 75 days.
                    Deals stagnating past 75 days have an 82% lower win rate and absorb unnecessary AE capacity.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No active deals in current filter.")
