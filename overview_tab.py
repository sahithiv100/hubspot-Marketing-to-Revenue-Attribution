"""
Executive Overview & Funnel Value Leak Detector Tab.
Displays top-level business KPIs, the full interactive exposure-to-revenue funnel,
ranked funnel value leaks, drop-off friction heatmap, and Manager Question 1.
"""

import streamlit as st
import pandas as pd
from ui.components import render_kpi_card, render_manager_question, render_causal_disclaimer
from ui.charts import plot_interactive_funnel, plot_waterfall_value_leaks, plot_dropoff_heatmap
from models.funnel_analysis import compute_funnel_metrics, rank_funnel_value_leaks, compute_channel_dropoff_heatmap

def render_overview_tab(df_journeys: pd.DataFrame, df_touchpoints: pd.DataFrame, df_deals: pd.DataFrame):
    st.markdown("### 📊 Executive Funnel & Pipeline Leak Detector")
    st.markdown(
        "Trace synthetic prospective buyer journeys from initial campaign exposure through website sessions, "
        "MQL/SQL qualification, opportunity creation, and closed ARR. Locate exactly where pipeline friction destroys value."
    )

    total_spend = float(df_touchpoints["cost"].sum())
    funnel_df, unit_econ = compute_funnel_metrics(df_journeys, total_spend)
    df_leaks = rank_funnel_value_leaks(df_journeys, df_deals)
    df_heatmap = compute_channel_dropoff_heatmap(df_journeys)

    # Top KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(render_kpi_card("Total Marketing Spend", f"${unit_econ['total_spend']:,.0f}", f"{len(df_touchpoints):,} touchpoints", "neutral"), unsafe_allow_html=True)
    with col2:
        st.markdown(render_kpi_card("Closed Won Revenue", f"${unit_econ['total_revenue']:,.0f}", f"{unit_econ['n_won']} closed deals", "positive"), unsafe_allow_html=True)
    with col3:
        st.markdown(render_kpi_card("Blended ROAS", f"{unit_econ['roas']:.2f}x", "Gross ARR / Ad Spend", "positive" if unit_econ['roas'] > 1.5 else "negative"), unsafe_allow_html=True)
    with col4:
        st.markdown(render_kpi_card("Cost Per SQL (CPQL)", f"${unit_econ['cpsql']:,.0f}", f"{unit_econ['n_sql']} sales qualified", "neutral"), unsafe_allow_html=True)
    with col5:
        st.markdown(render_kpi_card("Opportunity Win Rate", f"{unit_econ['win_rate']:.1f}%", f"Avg ACV ${unit_econ['avg_won_acv']:,.0f}", "positive" if unit_econ['win_rate'] > 25 else "neutral"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Manager Question 1
    top_leak = df_leaks.iloc[0]
    render_manager_question(
        question_num=1,
        question="Where is our biggest drop-off and revenue leak in the funnel?",
        takeaway=f"The largest absolute value loss occurs at the <b>{top_leak['stage_transition']}</b> transition, leaking an estimated <b>${top_leak['estimated_value_lost']:,.0f}</b> in downstream ARR.",
        details=f"Out of {unit_econ['n_mql']} MQLs generated, {top_leak['dropped_count']} were dropped ({top_leak['drop_rate_pct']}% drop-off rate). Primary operational bottleneck: {top_leak['primary_driver']}. Accountable Owner: {top_leak['owner']}."
    )

    # Interactive Funnel & Value Leak Side-by-Side
    c_left, c_right = st.columns([1.1, 1.0])
    with c_left:
        st.plotly_chart(plot_interactive_funnel(funnel_df), use_container_width=True)
    with c_right:
        st.plotly_chart(plot_waterfall_value_leaks(df_leaks), use_container_width=True)

    # Ranked Leaks Table
    st.markdown("#### 🔍 Prioritized Funnel Value Leak Matrix")
    display_leaks = df_leaks.copy()
    display_leaks["estimated_value_lost"] = display_leaks["estimated_value_lost"].apply(lambda x: f"${x:,.0f}")
    display_leaks["unit_value_at_risk"] = display_leaks["unit_value_at_risk"].apply(lambda x: f"${x:,.2f}")
    display_leaks["drop_rate_pct"] = display_leaks["drop_rate_pct"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(
        display_leaks[["rank", "stage_transition", "funnel_step", "dropped_count", "drop_rate_pct", "unit_value_at_risk", "estimated_value_lost", "primary_driver", "owner", "priority"]],
        use_container_width=True,
        hide_index=True
    )

    # Heatmap of Drop-offs by Channel
    st.markdown("#### 🗺️ Funnel Drop-off Friction Heatmap by First-Touch Channel")
    st.markdown("Darker purple indicates higher percentage of prospective accounts abandoning at that transition.")
    st.plotly_chart(plot_dropoff_heatmap(df_heatmap), use_container_width=True)

    render_causal_disclaimer()
