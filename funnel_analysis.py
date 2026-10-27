"""
Funnel Analytics and Value Leak Engine.
Computes conversion rates, unit economics (CPL, CPQL, CAC), stage durations,
funnel value leaks, and SLA response impact.
"""

import numpy as np
import pandas as pd

def compute_funnel_metrics(df_journeys: pd.DataFrame, total_spend: float):
    """
    Computes rigorous stage-by-stage funnel metrics from Leads to Closed Won.
    """
    n_leads = len(df_journeys)
    n_mql = int(df_journeys["is_mql"].sum())
    n_sql = int(df_journeys["is_sql"].sum())
    n_opp = int(df_journeys["is_opp"].sum())
    n_won = int(df_journeys["is_won"].sum())

    total_revenue = float(df_journeys["closed_revenue"].sum())
    avg_won_acv = (total_revenue / n_won) if n_won > 0 else 0.0

    # Top of funnel estimated traffic & impressions
    # Realistic B2B SaaS ratios: ~10x website sessions per lead, ~15x ad impressions per session
    n_sessions = n_leads * 12
    n_impressions = n_sessions * 15

    stages = [
        {"stage": "1. Ad Impressions & Traffic", "count": n_impressions, "level": 1},
        {"stage": "2. Website Sessions", "count": n_sessions, "level": 2},
        {"stage": "3. Leads (Form & Free Tier)", "count": n_leads, "level": 3},
        {"stage": "4. Marketing Qualified (MQL)", "count": n_mql, "level": 4},
        {"stage": "5. Sales Qualified (SQL)", "count": n_sql, "level": 5},
        {"stage": "6. Sales Opportunity (Deal)", "count": n_opp, "level": 6},
        {"stage": "7. Closed Won Customer", "count": n_won, "level": 7}
    ]

    funnel_df = pd.DataFrame(stages)
    funnel_df["previous_count"] = funnel_df["count"].shift(1)
    funnel_df["step_conversion_rate"] = np.where(
        funnel_df["previous_count"].notnull() & (funnel_df["previous_count"] > 0),
        funnel_df["count"] / funnel_df["previous_count"],
        1.0
    )
    funnel_df["drop_off_count"] = np.where(
        funnel_df["previous_count"].notnull(),
        funnel_df["previous_count"] - funnel_df["count"],
        0
    )
    funnel_df["drop_off_rate"] = 1.0 - funnel_df["step_conversion_rate"]
    funnel_df["cumulative_cvr_from_leads"] = funnel_df["count"] / n_leads

    # Unit economics
    cpl = total_spend / n_leads if n_leads > 0 else 0.0
    cpmql = total_spend / n_mql if n_mql > 0 else 0.0
    cpsql = total_spend / n_sql if n_sql > 0 else 0.0
    cpo = total_spend / n_opp if n_opp > 0 else 0.0
    cac = total_spend / n_won if n_won > 0 else 0.0
    win_rate = (n_won / n_opp) if n_opp > 0 else 0.0
    roas = total_revenue / total_spend if total_spend > 0 else 0.0

    unit_economics = {
        "total_spend": round(total_spend, 2),
        "total_revenue": round(total_revenue, 2),
        "cpl": round(cpl, 2),
        "cpmql": round(cpmql, 2),
        "cpsql": round(cpsql, 2),
        "cpo": round(cpo, 2),
        "cac": round(cac, 2),
        "win_rate": round(win_rate * 100, 1),
        "roas": round(roas, 2),
        "avg_won_acv": round(avg_won_acv, 2),
        "n_leads": n_leads,
        "n_mql": n_mql,
        "n_sql": n_sql,
        "n_opp": n_opp,
        "n_won": n_won
    }

    return funnel_df, unit_economics

def rank_funnel_value_leaks(df_journeys: pd.DataFrame, df_deals: pd.DataFrame):
    """
    Ranks the stages where the most dollar value leaks from the funnel.
    Evaluates:
    - Lead -> MQL drop-off (Top of funnel qualification leak)
    - MQL -> SQL drop-off (SDR SLA & qualification leak)
    - SQL -> Opp drop-off (Discovery call & BANT qualification leak)
    - Opp -> Won drop-off (Sales execution & competitive loss leak)
    """
    n_leads = len(df_journeys)
    n_mql = int(df_journeys["is_mql"].sum())
    n_sql = int(df_journeys["is_sql"].sum())
    n_opp = int(df_journeys["is_opp"].sum())
    n_won = int(df_journeys["is_won"].sum())

    total_revenue = float(df_journeys["closed_revenue"].sum())
    avg_deal_acv = (total_revenue / n_won) if n_won > 0 else 24000.0

    # Downstream realization probabilities:
    # Probability that a lead reaching stage X eventually becomes a Won Deal
    p_won_given_lead = n_won / n_leads if n_leads > 0 else 0.0
    p_won_given_mql = n_won / n_mql if n_mql > 0 else 0.0
    p_won_given_sql = n_won / n_sql if n_sql > 0 else 0.0
    p_won_given_opp = n_won / n_opp if n_opp > 0 else 0.0

    # Expected dollar realization value per unit dropped
    val_per_lead = p_won_given_lead * avg_deal_acv
    val_per_mql = p_won_given_mql * avg_deal_acv
    val_per_sql = p_won_given_sql * avg_deal_acv
    val_per_opp = p_won_given_opp * avg_deal_acv

    dropped_leads = n_leads - n_mql
    dropped_mqls = n_mql - n_sql
    dropped_sqls = n_sql - n_opp
    dropped_opps = n_opp - n_won

    leaks = [
        {
            "stage_transition": "MQL -> SQL (SDR Qualification)",
            "funnel_step": "Middle Funnel",
            "dropped_count": dropped_mqls,
            "drop_rate_pct": round((dropped_mqls / n_mql * 100) if n_mql > 0 else 0, 1),
            "unit_value_at_risk": round(val_per_mql, 2),
            "estimated_value_lost": round(dropped_mqls * val_per_mql, 0),
            "primary_driver": "SDR Response Time SLA Breach & Contact Rate",
            "owner": "Sales Development (SDR Ops)",
            "priority": "Critical"
        },
        {
            "stage_transition": "Opportunity -> Closed Won",
            "funnel_step": "Bottom Funnel",
            "dropped_count": dropped_opps,
            "drop_rate_pct": round((dropped_opps / n_opp * 100) if n_opp > 0 else 0, 1),
            "unit_value_at_risk": round(val_per_opp, 2),
            "estimated_value_lost": round(dropped_opps * val_per_opp, 0),
            "primary_driver": "Competitor Displacement & Budget Freeze",
            "owner": "Account Executives / Sales Leadership",
            "priority": "High"
        },
        {
            "stage_transition": "Lead -> MQL (Inbound Qualification)",
            "funnel_step": "Top Funnel",
            "dropped_count": dropped_leads,
            "drop_rate_pct": round((dropped_leads / n_leads * 100) if n_leads > 0 else 0, 1),
            "unit_value_at_risk": round(val_per_lead, 2),
            "estimated_value_lost": round(dropped_leads * val_per_lead, 0),
            "primary_driver": "Low Intent Forms, Student/Blogger Traffic, Mismatched ICP",
            "owner": "Demand Generation & Content Strategy",
            "priority": "High"
        },
        {
            "stage_transition": "SQL -> Opportunity (AE Discovery)",
            "funnel_step": "Mid-to-Late Funnel",
            "dropped_count": dropped_sqls,
            "drop_rate_pct": round((dropped_sqls / n_sql * 100) if n_sql > 0 else 0, 1),
            "unit_value_at_risk": round(val_per_sql, 2),
            "estimated_value_lost": round(dropped_sqls * val_per_sql, 0),
            "primary_driver": "Budget Misalignment & Unconfirmed Timeline",
            "owner": "RevOps & Sales Enablement",
            "priority": "Medium"
        }
    ]

    df_leaks = pd.DataFrame(leaks)
    df_leaks = df_leaks.sort_values(by="estimated_value_lost", ascending=False).reset_index(drop=True)
    df_leaks["rank"] = df_leaks.index + 1

    return df_leaks

def compute_channel_dropoff_heatmap(df_journeys: pd.DataFrame):
    """
    Calculates drop-off rates across funnel stages segmented by First-Touch Channel.
    Returns a dataframe ready for heatmap visualization.
    """
    grouped = df_journeys.groupby("first_touch_channel").agg(
        leads=("journey_id", "count"),
        mqls=("is_mql", "sum"),
        sqls=("is_sql", "sum"),
        opps=("is_opp", "sum"),
        wons=("is_won", "sum")
    ).reset_index()

    grouped["lead_to_mql_drop"] = np.round((1.0 - (grouped["mqls"] / grouped["leads"])) * 100, 1)
    grouped["mql_to_sql_drop"] = np.round((1.0 - (grouped["sqls"] / grouped["mqls"].replace(0, np.nan))) * 100, 1)
    grouped["sql_to_opp_drop"] = np.round((1.0 - (grouped["opps"] / grouped["sqls"].replace(0, np.nan))) * 100, 1)
    grouped["opp_to_won_drop"] = np.round((1.0 - (grouped["wons"] / grouped["opps"].replace(0, np.nan))) * 100, 1)
    grouped["overall_lead_to_won_cvr"] = np.round((grouped["wons"] / grouped["leads"]) * 100, 2)

    return grouped

def analyze_sdr_sla(df_journeys: pd.DataFrame):
    """
    Segments journeys by SDR Response SLA bucket and calculates
    qualification rate, win rate, and sales velocity.
    """
    mql_df = df_journeys[df_journeys["is_mql"]].copy()

    def get_sla_bucket(hrs):
        if hrs <= 1.0:
            return "1. Ultra-Fast (< 1 Hour)"
        elif hrs <= 4.0:
            return "2. Same Morning/Day (1 - 4 Hours)"
        elif hrs <= 24.0:
            return "3. Within 24 Hours (4 - 24 Hours)"
        else:
            return "4. SLA Breach (> 24 Hours)"

    mql_df["sla_tier"] = mql_df["sdr_response_hours"].apply(get_sla_bucket)

    sla_summary = mql_df.groupby("sla_tier").agg(
        mql_count=("journey_id", "count"),
        sql_count=("is_sql", "sum"),
        opp_count=("is_opp", "sum"),
        won_count=("is_won", "sum"),
        total_revenue=("closed_revenue", "sum"),
        avg_lead_score=("lead_score", "mean")
    ).reset_index()

    sla_summary["sql_conversion_rate"] = np.round((sla_summary["sql_count"] / sla_summary["mql_count"]) * 100, 1)
    sla_summary["mql_to_won_rate"] = np.round((sla_summary["won_count"] / sla_summary["mql_count"]) * 100, 1)
    sla_summary["avg_revenue_per_mql"] = np.round(sla_summary["total_revenue"] / sla_summary["mql_count"], 0)

    return sla_summary
