"""
Interactive Plotly Visualizations for HubSpot Marketing Attribution Prototype.
All charts are styled consistently in Dark Navy / Charcoal with purple/violet accents.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Palette constants
BG_COLOR = "#161B26"
PAPER_COLOR = "#0E1117"
TEXT_COLOR = "#E2E8F0"
GRID_COLOR = "#232D42"
PURPLE_PRIMARY = "#8B5CF6"
PURPLE_LIGHT = "#A78BFA"
INDIGO_ACCENT = "#6366F1"
TEAL_ACCENT = "#14B8A6"
CORAL_ACCENT = "#F43F5E"
AMBER_ACCENT = "#F59E0B"

def _apply_theme(fig: go.Figure, title: str = "", height: int = 420):
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>" if title else "",
            "font": {"color": "#F8FAFC", "size": 15},
            "x": 0.02,
            "y": 0.95
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#161B26",
        font={"color": TEXT_COLOR, "family": "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto"},
        height=height,
        margin={"l": 40, "r": 30, "t": 50, "b": 40},
        xaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color="#94A3B8")
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color="#94A3B8")
        ),
        legend=dict(
            bgcolor="rgba(22, 27, 38, 0.8)",
            bordercolor=GRID_COLOR,
            font=dict(color=TEXT_COLOR)
        )
    )
    return fig

def plot_interactive_funnel(df_funnel: pd.DataFrame):
    """
    Renders an interactive stage-by-stage funnel diagram with drop-off markers.
    """
    stages = df_funnel["stage"].tolist()
    counts = df_funnel["count"].tolist()
    cvrs = df_funnel["step_conversion_rate"].tolist()

    hover_text = [
        f"<b>{s}</b><br>Volume: {c:,}<br>Step CVR: {cvr*100:.1f}%"
        for s, c, cvr in zip(stages, counts, cvrs)
    ]

    fig = go.Figure(go.Funnel(
        y=stages,
        x=counts,
        textinfo="value+percent previous",
        textposition="inside",
        hovertext=hover_text,
        hoverinfo="text",
        marker=dict(
            color=["#4C1D95", "#5B21B6", "#6D28D9", "#7C3AED", "#8B5CF6", "#A78BFA", "#C4B5FD"],
            line=dict(width=1.5, color="#2E1065")
        ),
        connector=dict(line=dict(color="#475569", width=1.5, dash="dot"))
    ))

    _apply_theme(fig, "Customer Journey Stage Progression (Traffic to Closed Won)", height=450)
    return fig

def plot_attribution_comparison(df_channel_attr: pd.DataFrame):
    """
    Grouped bar chart comparing First-Touch, Last-Touch, Linear, and U-Shaped Attributed Revenue.
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="First-Touch (Discovery)",
        x=df_channel_attr["channel"],
        y=df_channel_attr["revenue_first_touch"],
        marker_color="#8B5CF6"
    ))
    fig.add_trace(go.Bar(
        name="Last-Touch (Conversion)",
        x=df_channel_attr["channel"],
        y=df_channel_attr["revenue_last_touch"],
        marker_color="#38BDF8"
    ))
    fig.add_trace(go.Bar(
        name="Linear (Equal Share)",
        x=df_channel_attr["channel"],
        y=df_channel_attr["revenue_linear"],
        marker_color="#F59E0B"
    ))
    fig.add_trace(go.Bar(
        name="U-Shaped (Position-Based)",
        x=df_channel_attr["channel"],
        y=df_channel_attr["revenue_u_shaped"],
        marker_color="#10B981"
    ))

    fig.update_layout(barmode="group")
    fig.update_yaxes(title="Attributed Revenue ($)", tickprefix="$")
    fig.update_xaxes(tickangle=-25)
    _apply_theme(fig, "Revenue Attribution by Model Across Marketing Channels", height=450)
    return fig

def plot_channel_roas_bubble(df_channel_attr: pd.DataFrame):
    """
    Spend vs Attributed Revenue bubble chart highlighting ROAS efficiency.
    """
    fig = px.scatter(
        df_channel_attr,
        x="total_spend",
        y="revenue_u_shaped",
        size="won_deals_u_shaped",
        color="channel",
        hover_name="channel",
        hover_data={
            "total_spend": ":$,.0f",
            "revenue_u_shaped": ":$,.0f",
            "roas_u_shaped": ":.2f",
            "won_deals_u_shaped": ":.1f"
        },
        labels={
            "total_spend": "Total Channel Spend ($)",
            "revenue_u_shaped": "U-Shaped Attributed Revenue ($)",
            "won_deals_u_shaped": "Attributed Won Deals"
        }
    )

    # 1.0 ROAS break-even line
    max_val = max(df_channel_attr["total_spend"].max(), df_channel_attr["revenue_u_shaped"].max()) * 1.05
    fig.add_trace(go.Scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode="lines",
        name="Break-Even (1.0x ROAS)",
        line=dict(color="#64748B", dash="dash", width=1.5)
    ))

    fig.update_xaxes(tickprefix="$")
    fig.update_yaxes(tickprefix="$")
    _apply_theme(fig, "Marketing Spend vs Attributed Revenue (Bubble Size = Won Deals)", height=420)
    return fig

def plot_waterfall_value_leaks(df_leaks: pd.DataFrame):
    """
    Horizontal bar chart ranking dollar value lost at each stage of the funnel.
    """
    df_sorted = df_leaks.sort_values(by="estimated_value_lost", ascending=True)

    fig = go.Figure(go.Bar(
        y=df_sorted["stage_transition"],
        x=df_sorted["estimated_value_lost"],
        orientation="h",
        marker=dict(
            color=df_sorted["estimated_value_lost"],
            colorscale=[[0, "#6366F1"], [0.5, "#EC4899"], [1.0, "#EF4444"]],
            showscale=False
        ),
        text=df_sorted["estimated_value_lost"].apply(lambda v: f"${v:,.0f} lost"),
        textposition="inside",
        hovertext=[
            f"<b>{row['stage_transition']}</b><br>Value Lost: ${row['estimated_value_lost']:,.0f}<br>Dropped Count: {row['dropped_count']:,}<br>Primary Driver: {row['primary_driver']}"
            for _, row in df_sorted.iterrows()
        ],
        hoverinfo="text"
    ))

    fig.update_xaxes(title="Estimated Realization Value Lost ($)", tickprefix="$")
    _apply_theme(fig, "Ranked Funnel Value Leaks (Downstream Realization Value Lost)", height=380)
    return fig

def plot_dropoff_heatmap(df_heatmap: pd.DataFrame):
    """
    Heatmap of stage drop-off percentage across marketing channels.
    """
    channels = df_heatmap["first_touch_channel"].tolist()
    stages = ["Lead -> MQL", "MQL -> SQL", "SQL -> Opp", "Opp -> Won"]
    z_data = [
        df_heatmap["lead_to_mql_drop"].tolist(),
        df_heatmap["mql_to_sql_drop"].tolist(),
        df_heatmap["sql_to_opp_drop"].tolist(),
        df_heatmap["opp_to_won_drop"].tolist()
    ]
    # Transpose so channels are on Y, stages on X
    z_matrix = np.array(z_data).T

    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=stages,
        y=channels,
        colorscale="Purples",
        reversescale=False,
        text=[[f"{val:.1f}%" for val in row] for row in z_matrix],
        texttemplate="%{text}",
        hoverongaps=False,
        colorbar=dict(title="Drop-off %", tickfont=dict(color=TEXT_COLOR))
    ))

    _apply_theme(fig, "Drop-Off Friction Heatmap (% Lost per Stage by Initial Channel)", height=420)
    return fig

def plot_sdr_sla_conversion(df_sla: pd.DataFrame):
    """
    Bar chart showing the steep decay in SQL conversion and Revenue per MQL as SDR response time increases.
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_sla["sla_tier"],
        y=df_sla["sql_conversion_rate"],
        name="SQL Conversion Rate (%)",
        marker_color=["#10B981", "#3B82F6", "#F59E0B", "#EF4444"],
        text=df_sla["sql_conversion_rate"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        yaxis="y1"
    ))

    fig.add_trace(go.Scatter(
        x=df_sla["sla_tier"],
        y=df_sla["avg_revenue_per_mql"],
        name="Avg Revenue per MQL ($)",
        mode="lines+markers",
        line=dict(color="#A78BFA", width=3),
        marker=dict(size=10, color="#C4B5FD"),
        yaxis="y2"
    ))

    fig.update_layout(
        yaxis=dict(title="SQL Conversion Rate (%)", range=[0, 60]),
        yaxis2=dict(
            title="Avg Revenue per MQL ($)",
            overlaying="y",
            side="right",
            tickprefix="$",
            gridcolor="rgba(0,0,0,0)"
        )
    )

    _apply_theme(fig, "Impact of SDR Response Time SLA on Qualification & Revenue", height=420)
    return fig

def plot_lead_score_win_rate(df_journeys: pd.DataFrame):
    """
    Lead Score distribution segmented by deal outcome (Won vs Lost/Dropped).
    """
    fig = go.Figure()

    won_scores = df_journeys[df_journeys["is_won"]]["lead_score"]
    lost_scores = df_journeys[~df_journeys["is_won"]]["lead_score"]

    fig.add_trace(go.Box(
        y=won_scores,
        name="Closed Won Accounts",
        marker_color="#10B981",
        boxmean=True
    ))
    fig.add_trace(go.Box(
        y=lost_scores,
        name="Unconverted / Lost Leads",
        marker_color="#F43F5E",
        boxmean=True
    ))

    fig.update_yaxes(title="Predictive Lead Fit Score (1 - 100)")
    _apply_theme(fig, "HubSpot Lead Fit Score Distribution by Journey Outcome", height=380)
    return fig
