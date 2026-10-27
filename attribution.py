"""
Attribution Computation Engine.
Calculates First-Touch, Last-Touch, Linear, U-Shaped (Position-based), and Time-Decay Attribution.

IMPORTANT GOVERNANCE & METHODOLOGICAL DISCLOSURE:
Attribution weights are heuristic accounting allocations of realized pipeline and revenue.
They describe correlation along the observed customer journey. They DO NOT prove causal
incrementality or counterfactual lift. Decisions to defund channels should be validated
via controlled geo/holdout incrementality experiments.
"""

import numpy as np
import pandas as pd

def compute_attribution_weights(df_touchpoints: pd.DataFrame, df_journeys: pd.DataFrame, half_life_days: float = 14.0):
    """
    Computes touchpoint-level credit weights for 5 attribution models:
    - first_touch_weight
    - last_touch_weight
    - linear_weight
    - u_shaped_weight
    - time_decay_weight

    Attaches journey revenue to touchpoints and calculates attributed revenue.
    """
    # Merge journey-level revenue and outcome onto touchpoints
    j_sub = df_journeys[["journey_id", "closed_revenue", "is_won", "is_opp"]].copy()
    tp_df = df_touchpoints.merge(j_sub, on="journey_id", how="left")

    # Sort touchpoints chronologically per journey
    tp_df = tp_df.sort_values(by=["journey_id", "timestamp"]).reset_index(drop=True)

    # Compute sequence indexing per journey
    tp_df["touch_rank"] = tp_df.groupby("journey_id").cumcount() + 1
    tp_df["total_touches"] = tp_df.groupby("journey_id")["touchpoint_id"].transform("count")

    # 1. First-Touch Weight (1.0 for rank == 1, else 0)
    tp_df["weight_first_touch"] = np.where(tp_df["touch_rank"] == 1, 1.0, 0.0)

    # 2. Last-Touch Weight (1.0 for rank == total_touches, else 0)
    tp_df["weight_last_touch"] = np.where(tp_df["touch_rank"] == tp_df["total_touches"], 1.0, 0.0)

    # 3. Linear Weight (1 / N)
    tp_df["weight_linear"] = 1.0 / tp_df["total_touches"]

    # 4. U-Shaped (Position-Based): 40% First, 40% Last, 20% Middle
    def calc_u_shaped(row):
        n = row["total_touches"]
        r = row["touch_rank"]
        if n == 1:
            return 1.0
        elif n == 2:
            return 0.5
        else:
            if r == 1:
                return 0.40
            elif r == n:
                return 0.40
            else:
                return 0.20 / (n - 2)

    tp_df["weight_u_shaped"] = tp_df.apply(calc_u_shaped, axis=1)

    # 5. Time-Decay: Exponential decay based on days before last touch
    # Weight = 2^(-(t_last - t) / half_life)
    max_times = tp_df.groupby("journey_id")["timestamp"].transform("max")
    days_to_last = (max_times - tp_df["timestamp"]).dt.total_seconds() / 86400.0
    raw_decay = np.power(2.0, -days_to_last / half_life_days)
    tp_df["raw_decay"] = raw_decay
    sum_decay = tp_df.groupby("journey_id")["raw_decay"].transform("sum")
    tp_df["weight_time_decay"] = np.where(sum_decay > 0, tp_df["raw_decay"] / sum_decay, 1.0 / tp_df["total_touches"])
    tp_df.drop(columns=["raw_decay"], inplace=True)

    # Compute Attributed Revenue for each model
    for model in ["first_touch", "last_touch", "linear", "u_shaped", "time_decay"]:
        tp_df[f"attr_rev_{model}"] = tp_df[f"weight_{model}"] * tp_df["closed_revenue"]
        tp_df[f"attr_won_{model}"] = tp_df[f"weight_{model}"] * tp_df["is_won"].astype(float)
        tp_df[f"attr_opp_{model}"] = tp_df[f"weight_{model}"] * tp_df["is_opp"].astype(float)

    return tp_df

def summarize_channel_attribution(attributed_touchpoints: pd.DataFrame):
    """
    Aggregates attribution results by channel across all models,
    including spend, attributed revenue, ROAS, and customer acquisition.
    """
    models = ["first_touch", "last_touch", "linear", "u_shaped", "time_decay"]

    # Channel spend is the sum of touchpoint costs
    channel_spend = attributed_touchpoints.groupby("channel")["cost"].sum().rename("total_spend")
    channel_touches = attributed_touchpoints.groupby("channel")["touchpoint_id"].count().rename("touchpoint_volume")

    summary_df = pd.concat([channel_spend, channel_touches], axis=1)

    for m in models:
        rev_m = attributed_touchpoints.groupby("channel")[f"attr_rev_{m}"].sum().rename(f"revenue_{m}")
        won_m = attributed_touchpoints.groupby("channel")[f"attr_won_{m}"].sum().rename(f"won_deals_{m}")
        summary_df = summary_df.join(rev_m).join(won_m)
        summary_df[f"roas_{m}"] = np.where(
            summary_df["total_spend"] > 0,
            summary_df[f"revenue_{m}"] / summary_df["total_spend"],
            0.0
        )
        summary_df[f"cac_{m}"] = np.where(
            summary_df[f"won_deals_{m}"] > 0,
            summary_df["total_spend"] / summary_df[f"won_deals_{m}"],
            0.0
        )

    summary_df = summary_df.reset_index()

    # Calculate upper-funnel vs lower-funnel bias indicator:
    # First-Touch Revenue vs Last-Touch Revenue
    summary_df["ftl_ratio"] = np.where(
        summary_df["revenue_last_touch"] > 0,
        summary_df["revenue_first_touch"] / summary_df["revenue_last_touch"],
        1.0
    )

    return summary_df

def summarize_campaign_attribution(attributed_touchpoints: pd.DataFrame):
    """
    Aggregates attribution metrics at the campaign level.
    """
    models = ["first_touch", "last_touch", "linear", "u_shaped", "time_decay"]
    camp_summary = attributed_touchpoints.groupby(["channel", "campaign_name"]).agg(
        total_touches=("touchpoint_id", "count"),
        total_spend=("cost", "sum"),
        revenue_first_touch=("attr_rev_first_touch", "sum"),
        revenue_last_touch=("attr_rev_last_touch", "sum"),
        revenue_linear=("attr_rev_linear", "sum"),
        revenue_u_shaped=("attr_rev_u_shaped", "sum"),
        revenue_time_decay=("attr_rev_time_decay", "sum"),
        won_deals_u_shaped=("attr_won_u_shaped", "sum")
    ).reset_index()

    camp_summary["roas_u_shaped"] = np.where(
        camp_summary["total_spend"] > 0,
        camp_summary["revenue_u_shaped"] / camp_summary["total_spend"],
        0.0
    )
    camp_summary["roas_first_touch"] = np.where(
        camp_summary["total_spend"] > 0,
        camp_summary["revenue_first_touch"] / camp_summary["total_spend"],
        0.0
    )
    camp_summary["roas_last_touch"] = np.where(
        camp_summary["total_spend"] > 0,
        camp_summary["revenue_last_touch"] / camp_summary["total_spend"],
        0.0
    )

    return camp_summary
