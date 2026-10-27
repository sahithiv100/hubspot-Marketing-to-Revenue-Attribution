"""
UI and Chart rendering validation script.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.synthetic_generator import generate_synthetic_data
from models.attribution import compute_attribution_weights, summarize_channel_attribution
from models.funnel_analysis import compute_funnel_metrics, rank_funnel_value_leaks, compute_channel_dropoff_heatmap, analyze_sdr_sla
from ui.charts import (
    plot_interactive_funnel,
    plot_attribution_comparison,
    plot_channel_roas_bubble,
    plot_waterfall_value_leaks,
    plot_dropoff_heatmap,
    plot_sdr_sla_conversion,
    plot_lead_score_win_rate
)

def test_charts():
    print("Testing chart rendering...")
    tp, jrn, deals, camps = generate_synthetic_data(seed=42, num_journeys=300)
    total_spend = float(tp["cost"].sum())
    funnel_df, econ = compute_funnel_metrics(jrn, total_spend)
    leaks = rank_funnel_value_leaks(jrn, deals)
    heatmap = compute_channel_dropoff_heatmap(jrn)
    sla = analyze_sdr_sla(jrn)
    attr_tp = compute_attribution_weights(tp, jrn)
    summary_ch = summarize_channel_attribution(attr_tp)

    f1 = plot_interactive_funnel(funnel_df)
    f2 = plot_attribution_comparison(summary_ch)
    f3 = plot_channel_roas_bubble(summary_ch)
    f4 = plot_waterfall_value_leaks(leaks)
    f5 = plot_dropoff_heatmap(heatmap)
    f6 = plot_sdr_sla_conversion(sla)
    f7 = plot_lead_score_win_rate(jrn)

    print("All 7 Plotly charts created successfully!")

if __name__ == "__main__":
    test_charts()
