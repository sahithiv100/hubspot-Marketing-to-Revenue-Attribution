"""
Scenario Simulator & What-If Optimizer Engine.
Simulates business impact of:
1. Marketing budget reallocation across channels
2. Landing page conversion rate optimization (CRO)
3. Sales SDR response time SLA compliance
4. Opportunity win rate enhancement
"""

import numpy as np
import pandas as pd

def simulate_scenario(
    df_journeys: pd.DataFrame,
    df_touchpoints: pd.DataFrame,
    budget_shift_pct: float = 0.0,
    source_channel: str = "Paid Social - LinkedIn",
    target_channel: str = "Paid Search - NonBrand",
    landing_page_cvr_lift_pct: float = 0.0,
    sdr_sla_fast_share_pct: float = 25.0, # Percentage of MQLs contacted in < 1h
    ae_win_rate_lift_pct: float = 0.0
):
    """
    Recalculates pipeline, deals, revenue, and ROAS under simulated adjustments.
    Returns baseline vs simulated metrics and delta comparisons.
    """
    # Baseline calculations
    base_spend = float(df_touchpoints["cost"].sum())
    base_leads = len(df_journeys)
    base_mqls = int(df_journeys["is_mql"].sum())
    base_sqls = int(df_journeys["is_sql"].sum())
    base_opps = int(df_journeys["is_opp"].sum())
    base_won = int(df_journeys["is_won"].sum())
    base_revenue = float(df_journeys["closed_revenue"].sum())
    base_roas = (base_revenue / base_spend) if base_spend > 0 else 0.0
    base_cac = (base_spend / base_won) if base_won > 0 else 0.0
    avg_acv = (base_revenue / base_won) if base_won > 0 else 24000.0

    # 1. Budget shift impact:
    # Estimate channel unit acquisition efficiency
    source_spend = float(df_touchpoints[df_touchpoints["channel"] == source_channel]["cost"].sum())
    shift_amount = source_spend * (budget_shift_pct / 100.0)

    # Cost per lead on target vs source
    # If we shift budget to higher ROAS channel, lead efficiency improves
    channel_spend = df_touchpoints.groupby("channel")["cost"].sum()
    channel_leads = df_journeys.groupby("first_touch_channel")["journey_id"].count()

    cpl_source = (channel_spend.get(source_channel, 50.0) / channel_leads.get(source_channel, 10.0)) if channel_leads.get(source_channel, 0) > 0 else 50.0
    cpl_target = (channel_spend.get(target_channel, 40.0) / channel_leads.get(target_channel, 10.0)) if channel_leads.get(target_channel, 0) > 0 else 40.0

    delta_leads_from_shift = (shift_amount / cpl_target) - (shift_amount / cpl_source) if cpl_target > 0 and cpl_source > 0 else 0

    # 2. Landing Page CVR Lift
    # Increases top-of-funnel lead and MQL yield
    sim_leads = max(10, int(base_leads * (1.0 + landing_page_cvr_lift_pct / 100.0) + delta_leads_from_shift))
    sim_mql_rate = (base_mqls / base_leads) * (1.0 + (landing_page_cvr_lift_pct * 0.4) / 100.0) if base_leads > 0 else 0.4
    sim_mqls = max(5, int(sim_leads * sim_mql_rate))

    # 3. SDR Response SLA impact:
    # Fast SLA (< 1h) converts to SQL at ~48%
    # Standard/delayed SLA converts at ~20%
    # User slider sets % of MQLs receiving < 1h ultra-fast response
    fast_fraction = np.clip(sdr_sla_fast_share_pct / 100.0, 0.0, 1.0)
    blended_sql_rate = (fast_fraction * 0.48) + ((1.0 - fast_fraction) * 0.20)
    sim_sqls = max(3, int(sim_mqls * blended_sql_rate))

    # 4. AE Opportunity & Win rate
    opp_conversion_rate = (base_opps / base_sqls) if base_sqls > 0 else 0.55
    sim_opps = max(2, int(sim_sqls * opp_conversion_rate))

    sim_win_rate = ((base_won / base_opps) if base_opps > 0 else 0.32) * (1.0 + ae_win_rate_lift_pct / 100.0)
    sim_win_rate = np.clip(sim_win_rate, 0.05, 0.85)
    sim_won = max(1, int(sim_opps * sim_win_rate))

    sim_spend = base_spend # Total budget preserved or reallocated
    sim_revenue = sim_won * avg_acv
    sim_roas = (sim_revenue / sim_spend) if sim_spend > 0 else 0.0
    sim_cac = (sim_spend / sim_won) if sim_won > 0 else 0.0

    delta_revenue = sim_revenue - base_revenue
    delta_roas = sim_roas - base_roas
    delta_won = sim_won - base_won
    delta_cac = sim_cac - base_cac

    results = {
        "baseline": {
            "spend": round(base_spend, 2),
            "leads": base_leads,
            "mqls": base_mqls,
            "sqls": base_sqls,
            "opps": base_opps,
            "won_deals": base_won,
            "revenue": round(base_revenue, 2),
            "roas": round(base_roas, 2),
            "cac": round(base_cac, 2)
        },
        "simulated": {
            "spend": round(sim_spend, 2),
            "leads": sim_leads,
            "mqls": sim_mqls,
            "sqls": sim_sqls,
            "opps": sim_opps,
            "won_deals": sim_won,
            "revenue": round(sim_revenue, 2),
            "roas": round(sim_roas, 2),
            "cac": round(sim_cac, 2)
        },
        "deltas": {
            "revenue": round(delta_revenue, 2),
            "revenue_pct": round((delta_revenue / base_revenue * 100) if base_revenue > 0 else 0, 1),
            "roas": round(delta_roas, 2),
            "won_deals": delta_won,
            "cac": round(delta_cac, 2)
        }
    }

    return results
