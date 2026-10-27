"""
What-If Scenario Simulator & Optimizer Tab.
Provides interactive controls to simulate budget reallocations, landing page CRO improvements,
SDR response SLA enforcement, and AE win-rate optimization with real-time recalculations and exports.
"""

import streamlit as st
import pandas as pd
from ui.components import render_kpi_card
from models.scenario_simulator import simulate_scenario

def render_scenario_tab(df_journeys: pd.DataFrame, df_touchpoints: pd.DataFrame):
    st.markdown("### 🎛️ What-If Scenario Simulator & Growth Optimizer")
    st.markdown(
        "Simulate the revenue and efficiency impact of strategic RevOps interventions: "
        "reallocating marketing spend, lifting landing page conversions, and enforcing SDR response SLAs."
    )

    channels = df_touchpoints["channel"].unique().tolist()

    # Control Levers in Columns
    st.markdown("#### ⚙️ Scenario Control Levers")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**1. Budget Reallocation**")
        source_ch = st.selectbox("From Channel", channels, index=min(2, len(channels)-1))
        target_ch = st.selectbox("To Channel", channels, index=min(1, len(channels)-1))
        shift_pct = st.slider("Budget Shift (%)", min_value=0, max_value=50, value=20, step=5)

    with col2:
        st.markdown("**2. Landing Page CRO Lift**")
        st.caption("Friction reduction / Form optimization")
        cro_lift_pct = st.slider("Conversion Rate Lift (%)", min_value=0, max_value=25, value=10, step=1)

    with col3:
        st.markdown("**3. Fast SDR SLA Compliance**")
        st.caption("% MQLs contacted in < 1 hour")
        sla_fast_share = st.slider("Fast Response Share (%)", min_value=10, max_value=90, value=65, step=5)

    with col4:
        st.markdown("**4. AE Win Rate Lift**")
        st.caption("Sales enablement / objection handling")
        ae_lift_pct = st.slider("AE Win Rate Lift (%)", min_value=0, max_value=20, value=5, step=1)

    # Run simulation
    sim_res = simulate_scenario(
        df_journeys=df_journeys,
        df_touchpoints=df_touchpoints,
        budget_shift_pct=shift_pct,
        source_channel=source_ch,
        target_channel=target_ch,
        landing_page_cvr_lift_pct=cro_lift_pct,
        sdr_sla_fast_share_pct=sla_fast_share,
        ae_win_rate_lift_pct=ae_lift_pct
    )

    base = sim_res["baseline"]
    sim = sim_res["simulated"]
    delta = sim_res["deltas"]

    st.markdown("<hr style='border-color: #232D42;'>", unsafe_allow_html=True)
    st.markdown("#### 📈 Projected Scenario Impact vs. Current Baseline")

    # Delta KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        delta_rev_sign = "+" if delta["revenue"] >= 0 else ""
        st.markdown(render_kpi_card(
            "Projected Closed ARR",
            f"${sim['revenue']:,.0f}",
            f"{delta_rev_sign}${delta['revenue']:,.0f} ({delta_rev_sign}{delta['revenue_pct']}%)",
            "positive" if delta["revenue"] >= 0 else "negative"
        ), unsafe_allow_html=True)
    with k2:
        delta_won_sign = "+" if delta["won_deals"] >= 0 else ""
        st.markdown(render_kpi_card(
            "Projected Won Customers",
            f"{sim['won_deals']:,}",
            f"{delta_won_sign}{delta['won_deals']} deals",
            "positive" if delta["won_deals"] >= 0 else "negative"
        ), unsafe_allow_html=True)
    with k3:
        delta_roas_sign = "+" if delta["roas"] >= 0 else ""
        st.markdown(render_kpi_card(
            "Projected Blended ROAS",
            f"{sim['roas']:.2f}x",
            f"{delta_roas_sign}{delta['roas']:.2f}x lift",
            "positive" if delta["roas"] >= 0 else "negative"
        ), unsafe_allow_html=True)
    with k4:
        delta_cac_sign = "-" if delta["cac"] <= 0 else "+"
        st.markdown(render_kpi_card(
            "Projected Blended CAC",
            f"${sim['cac']:,.0f}",
            f"${abs(delta['cac']):,.0f} cost per customer",
            "positive" if delta["cac"] <= 0 else "negative"
        ), unsafe_allow_html=True)

    # Detailed Comparison Table
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📊 Metric-by-Metric Scenario Comparison")

    comparison_data = [
        {"Funnel Stage / Metric": "Total Marketing Spend", "Current Baseline": f"${base['spend']:,.0f}", "Simulated Scenario": f"${sim['spend']:,.0f}", "Net Delta": f"${sim['spend']-base['spend']:,.0f}"},
        {"Funnel Stage / Metric": "Total Inbound Leads", "Current Baseline": f"{base['leads']:,}", "Simulated Scenario": f"{sim['leads']:,}", "Net Delta": f"+{sim['leads']-base['leads']:,}"},
        {"Funnel Stage / Metric": "Marketing Qualified Leads (MQL)", "Current Baseline": f"{base['mqls']:,}", "Simulated Scenario": f"{sim['mqls']:,}", "Net Delta": f"+{sim['mqls']-base['mqls']:,}"},
        {"Funnel Stage / Metric": "Sales Qualified Leads (SQL)", "Current Baseline": f"{base['sqls']:,}", "Simulated Scenario": f"{sim['sqls']:,}", "Net Delta": f"+{sim['sqls']-base['sqls']:,}"},
        {"Funnel Stage / Metric": "Pipeline Opportunities (Deals)", "Current Baseline": f"{base['opps']:,}", "Simulated Scenario": f"{sim['opps']:,}", "Net Delta": f"+{sim['opps']-base['opps']:,}"},
        {"Funnel Stage / Metric": "Closed Won Deals", "Current Baseline": f"{base['won_deals']:,}", "Simulated Scenario": f"{sim['won_deals']:,}", "Net Delta": f"+{sim['won_deals']-base['won_deals']:,}"},
        {"Funnel Stage / Metric": "Closed Won Revenue (ARR)", "Current Baseline": f"${base['revenue']:,.0f}", "Simulated Scenario": f"${sim['revenue']:,.0f}", "Net Delta": f"+${delta['revenue']:,.0f}"},
        {"Funnel Stage / Metric": "Blended Marketing ROAS", "Current Baseline": f"{base['roas']:.2f}x", "Simulated Scenario": f"{sim['roas']:.2f}x", "Net Delta": f"+{delta['roas']:.2f}x"},
        {"Funnel Stage / Metric": "Customer Acquisition Cost (CAC)", "Current Baseline": f"${base['cac']:,.0f}", "Simulated Scenario": f"${sim['cac']:,.0f}", "Net Delta": f"${delta['cac']:,.0f}"}
    ]
    df_comp = pd.DataFrame(comparison_data)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # Download Scenario CSV
    csv_bytes = df_comp.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Scenario Simulation Results (CSV)",
        data=csv_bytes,
        file_name="hubspot_attribution_scenario_simulation.csv",
        mime="text/csv"
    )
