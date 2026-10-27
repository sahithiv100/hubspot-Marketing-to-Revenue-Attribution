"""
Journey Explorer & Multi-Touch Attribution Tab.
Allows deep-dive exploration of individual customer paths, side-by-side attribution
model comparison (First vs Last vs Linear vs U-Shaped vs Time-Decay), ROAS bubble analysis,
and Manager Question 2.
"""

import streamlit as st
import pandas as pd
from ui.components import render_kpi_card, render_manager_question, render_causal_disclaimer
from ui.charts import plot_attribution_comparison, plot_channel_roas_bubble
from models.attribution import compute_attribution_weights, summarize_channel_attribution

def render_journeys_tab(df_journeys: pd.DataFrame, df_touchpoints: pd.DataFrame):
    st.markdown("### 🧭 Customer Journey Explorer & Multi-Touch Attribution")
    st.markdown(
        "Trace multi-touch sequences across marketing interactions to understand how different attribution rules "
        "allocate credit between top-of-funnel discovery, mid-funnel nurture, and bottom-of-funnel deal creation."
    )

    # Compute attribution weights
    attributed_tp = compute_attribution_weights(df_touchpoints, df_journeys)
    df_channel_attr = summarize_channel_attribution(attributed_tp)

    # Manager Question 2
    render_manager_question(
        question_num=2,
        question="Which channel looks best on First-Touch vs Multi-Touch, and which one would be mistakenly cut?",
        takeaway="<b>Content Marketing / Blog</b> and <b>Organic Search (SEO)</b> receive up to <b>3.8x more revenue credit</b> under First-Touch and U-Shaped models than under Last-Touch.",
        details="Under single-touch Last-Touch attribution, Content & SEO appear unprofitable (ROAS < 0.6x) because buyers convert on Direct or Brand Search at the end. Defunding top-of-funnel content based on Last-Touch would choke the pipeline at its root."
    )

    # Attribution Comparison Visualizations
    st.plotly_chart(plot_attribution_comparison(df_channel_attr), use_container_width=True)

    c1, c2 = st.columns([1.1, 0.9])
    with c1:
        st.plotly_chart(plot_channel_roas_bubble(df_channel_attr), use_container_width=True)
    with c2:
        st.markdown("#### ⚖️ Channel Attribution Summary Table")
        disp_df = df_channel_attr[[
            "channel", "total_spend", "revenue_first_touch", "revenue_last_touch",
            "revenue_u_shaped", "roas_u_shaped", "ftl_ratio"
        ]].copy()
        disp_df["total_spend"] = disp_df["total_spend"].apply(lambda v: f"${v:,.0f}")
        disp_df["revenue_first_touch"] = disp_df["revenue_first_touch"].apply(lambda v: f"${v:,.0f}")
        disp_df["revenue_last_touch"] = disp_df["revenue_last_touch"].apply(lambda v: f"${v:,.0f}")
        disp_df["revenue_u_shaped"] = disp_df["revenue_u_shaped"].apply(lambda v: f"${v:,.0f}")
        disp_df["roas_u_shaped"] = disp_df["roas_u_shaped"].apply(lambda v: f"{v:.2f}x")
        disp_df["ftl_ratio"] = disp_df["ftl_ratio"].apply(lambda v: f"{v:.2f}x")
        disp_df.rename(columns={
            "channel": "Channel",
            "total_spend": "Spend",
            "revenue_first_touch": "First-Touch Rev",
            "revenue_last_touch": "Last-Touch Rev",
            "revenue_u_shaped": "U-Shaped Rev",
            "roas_u_shaped": "U-Shaped ROAS",
            "ftl_ratio": "First/Last Bias"
        }, inplace=True)
        st.dataframe(disp_df, use_container_width=True, hide_index=True)

    st.markdown("<hr style='border-color: #232D42;'>", unsafe_allow_html=True)

    # Individual Journey Deep-Dive Explorer
    st.markdown("### 🔎 Individual Account Journey Timeline Explorer")
    st.markdown("Select an account to view its full chronological touchpoint history, channels, and stage progression.")

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        stage_filter = st.selectbox(
            "Filter Account by Final Stage",
            ["All Stages", "Closed Won", "Closed Lost", "Disqualified SQL", "Unconverted MQL", "Unqualified Lead"],
            index=1
        )
    filtered_journeys = df_journeys if stage_filter == "All Stages" else df_journeys[df_journeys["final_stage"] == stage_filter]

    company_options = filtered_journeys["company_name"].unique().tolist()
    if not company_options:
        st.warning("No companies found matching this filter.")
        return

    with col_filter2:
        selected_company = st.selectbox("Select Account / Prospective Company", company_options)

    # Get Journey details
    journey_row = df_journeys[df_journeys["company_name"] == selected_company].iloc[0]
    j_id = journey_row["journey_id"]
    tps = df_touchpoints[df_touchpoints["journey_id"] == j_id].sort_values("timestamp")

    # Account Profile Card
    j_won_badge = "🟢 CLOSED WON" if journey_row["is_won"] else ("🔴 " + journey_row["final_stage"].upper())
    st.markdown(f"""
    <div style="background: #181E30; border: 1px solid #334155; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h4 style="margin: 0; color: #F8FAFC;">{journey_row['company_name']} ({j_id})</h4>
            <span style="font-weight: 700; color: {'#34D399' if journey_row['is_won'] else '#F87171'};">{j_won_badge}</span>
        </div>
        <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 6px;">
            Industry: <strong>{journey_row['industry']}</strong> | Region: <strong>{journey_row['region']}</strong> | Size: <strong>{journey_row['company_size']}</strong> | Lead Score: <strong>{journey_row['lead_score']}/100</strong><br>
            Touches: <strong>{len(tps)}</strong> | Journey Span: <strong>{journey_row['duration_days']} days</strong> | SDR Response Time: <strong>{journey_row['sdr_response_hours']} hrs</strong> | ARR: <strong>${journey_row['closed_revenue']:,.0f}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Render Chronological Timeline Table
    tp_display = tps[["timestamp", "channel", "campaign_name", "touchpoint_type", "stage_at_touch", "cost"]].copy()
    tp_display["timestamp"] = tp_display["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    tp_display["cost"] = tp_display["cost"].apply(lambda v: f"${v:,.2f}")
    tp_display.rename(columns={
        "timestamp": "Timestamp",
        "channel": "Channel",
        "campaign_name": "Campaign",
        "touchpoint_type": "Interaction Event",
        "stage_at_touch": "CRM Stage",
        "cost": "Cost"
    }, inplace=True)

    st.dataframe(tp_display, use_container_width=True, hide_index=True)

    render_causal_disclaimer()
