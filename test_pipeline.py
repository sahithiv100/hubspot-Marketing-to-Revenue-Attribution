"""
Self-test validation script for HubSpot Attribution Prototype.
"""
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.synthetic_generator import generate_synthetic_data
from models.attribution import compute_attribution_weights, summarize_channel_attribution
from models.funnel_analysis import compute_funnel_metrics, rank_funnel_value_leaks, compute_channel_dropoff_heatmap, analyze_sdr_sla
from models.scenario_simulator import simulate_scenario

def test_pipeline():
    print("1. Generating synthetic data...")
    tp, jrn, deals, camps = generate_synthetic_data(seed=42, num_journeys=600)
    assert len(tp) > 0, "No touchpoints generated!"
    assert len(jrn) == 600, f"Expected 600 journeys, got {len(jrn)}"
    assert len(deals) > 0, "No deals generated!"
    print(f"   -> Success: {len(tp)} touches, {len(jrn)} journeys, {len(deals)} deals.")

    print("2. Testing attribution engine...")
    attr_tp = compute_attribution_weights(tp, jrn)
    assert "weight_first_touch" in attr_tp.columns
    assert "weight_u_shaped" in attr_tp.columns
    assert "attr_rev_u_shaped" in attr_tp.columns
    summary_ch = summarize_channel_attribution(attr_tp)
    assert len(summary_ch) > 0
    print(f"   -> Success: Attribution computed for {len(summary_ch)} channels.")

    print("3. Testing funnel & value leak ranking...")
    total_spend = float(tp["cost"].sum())
    funnel_df, econ = compute_funnel_metrics(jrn, total_spend)
    assert len(funnel_df) == 7
    assert econ["roas"] > 0
    leaks = rank_funnel_value_leaks(jrn, deals)
    assert len(leaks) == 4
    print(f"   -> Success: Top leak identified as: {leaks.iloc[0]['stage_transition']} with ${leaks.iloc[0]['estimated_value_lost']:,.0f} lost.")

    print("4. Testing SLA velocity analysis...")
    sla = analyze_sdr_sla(jrn)
    assert len(sla) > 0
    print(f"   -> Success: SLA tiers analyzed ({len(sla)} tiers).")

    print("5. Testing scenario simulator...")
    sim = simulate_scenario(
        df_journeys=jrn,
        df_touchpoints=tp,
        budget_shift_pct=20,
        landing_page_cvr_lift_pct=10,
        sdr_sla_fast_share_pct=75,
        ae_win_rate_lift_pct=5
    )
    assert "baseline" in sim and "simulated" in sim and "deltas" in sim
    print(f"   -> Success: Simulated ARR lift = +${sim['deltas']['revenue']:,.0f} ({sim['deltas']['revenue_pct']}%)")

    print("\nALL BACKEND COMPUTATIONS & MODELS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_pipeline()
