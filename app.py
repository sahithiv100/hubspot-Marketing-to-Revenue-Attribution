"""
HubSpot Marketing-to-Revenue Attribution & Funnel Value Leak Detector.
Main Streamlit Application Entrypoint.

NOTE: All data used and displayed within this application is entirely synthetic
and generated for prototype evaluation purposes.
"""

import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="HubSpot | Marketing-to-Revenue Attribution & Funnel Leak Detector",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import internal modules
from data.synthetic_generator import generate_synthetic_data
from ui.components import apply_custom_theme, render_synthetic_banner
from ui.tabs.overview_tab import render_overview_tab
from ui.tabs.journeys_tab import render_journeys_tab
from ui.tabs.sla_velocity_tab import render_sla_velocity_tab
from ui.tabs.scenario_tab import render_scenario_tab
from ui.tabs.recommendations_tab import render_recommendations_tab
from ui.tabs.methodology_tab import render_methodology_tab
from ui.tabs.data_tab import render_data_tab

# Apply dark navy styling
apply_custom_theme()

# Top persistent synthetic banner
render_synthetic_banner()

# Initialize session state for random seed & parameters
if "random_seed" not in st.session_state:
    st.session_state.random_seed = 42

if "num_journeys" not in st.session_state:
    st.session_state.num_journeys = 1200

# Sidebar Configuration
st.sidebar.markdown("## 📈 HubSpot RevOps Engine")
st.sidebar.caption("Marketing Attribution & Pipeline Leak Analytics Prototype")
st.sidebar.markdown("<hr style='border-color: #232D42; margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)

st.sidebar.markdown("### 🎲 Synthetic Data Controls")
seed_input = st.sidebar.number_input("Random Seed (Reproducibility)", min_value=1, max_value=99999, value=st.session_state.random_seed)
sample_size = st.sidebar.slider("Sample Size (Buyer Journeys)", min_value=400, max_value=2500, value=st.session_state.num_journeys, step=100)

c_btn1, c_btn2 = st.sidebar.columns(2)
with c_btn1:
    if st.button("🔄 Regenerate Data", use_container_width=True):
        st.session_state.random_seed = int(seed_input) + np.random.randint(1, 100)
        st.session_state.num_journeys = sample_size
        st.cache_data.clear()
        st.rerun()

with c_btn2:
    if st.button("↩️ Reset Controls", use_container_width=True):
        st.session_state.random_seed = 42
        st.session_state.num_journeys = 1200
        st.cache_data.clear()
        st.rerun()

# Cached data generation function
@st.cache_data(show_spinner="Generating synthetic customer journeys and pipeline data...")
def get_cached_data(seed: int, num_journeys: int):
    return generate_synthetic_data(seed=seed, num_journeys=num_journeys)

df_touchpoints_raw, df_journeys_raw, df_deals_raw, df_campaign_costs_raw = get_cached_data(
    seed=st.session_state.random_seed,
    num_journeys=st.session_state.num_journeys
)

# Sidebar Global Filters
st.sidebar.markdown("<hr style='border-color: #232D42; margin-top: 15px; margin-bottom: 15px;'>", unsafe_allow_html=True)
st.sidebar.markdown("### 🔍 Global Dimension Filters")

all_channels = df_touchpoints_raw["channel"].unique().tolist()
selected_channels = st.sidebar.multiselect("Marketing Channels", all_channels, default=all_channels)

all_sizes = df_journeys_raw["company_size"].unique().tolist()
selected_sizes = st.sidebar.multiselect("Company Segment", all_sizes, default=all_sizes)

all_regions = df_journeys_raw["region"].unique().tolist()
selected_regions = st.sidebar.multiselect("Geographic Region", all_regions, default=all_regions)

min_score = st.sidebar.slider("Min Predictive Lead Fit Score", min_value=0, max_value=90, value=0, step=5)

# Filter datasets
filtered_journeys = df_journeys_raw[
    df_journeys_raw["first_touch_channel"].isin(selected_channels) &
    df_journeys_raw["company_size"].isin(selected_sizes) &
    df_journeys_raw["region"].isin(selected_regions) &
    (df_journeys_raw["lead_score"] >= min_score)
]

filtered_journey_ids = set(filtered_journeys["journey_id"])
filtered_touchpoints = df_touchpoints_raw[df_touchpoints_raw["journey_id"].isin(filtered_journey_ids)]
filtered_deals = df_deals_raw[df_deals_raw["journey_id"].isin(filtered_journey_ids)] if not df_deals_raw.empty else df_deals_raw

# Status display in sidebar
st.sidebar.markdown("<hr style='border-color: #232D42; margin-top: 15px; margin-bottom: 15px;'>", unsafe_allow_html=True)
st.sidebar.caption(
    f"Active Sample: **{len(filtered_journeys):,}** accounts | "
    f"**{len(filtered_touchpoints):,}** touches | "
    f"**{int(filtered_journeys['is_won'].sum())}** won deals"
)

# Main Navigation Tabs
tab_overview, tab_journeys, tab_sla, tab_scenario, tab_recs, tab_methodology, tab_data = st.tabs([
    "📊 Executive Funnel & Leaks",
    "🧭 Journeys & Attribution",
    "⚡ SLA & Velocity",
    "🎛️ Scenario Optimizer",
    "🎯 Action Matrix",
    "🔬 How Algorithm Works",
    "🗃️ Data Explorer & Exports"
])

with tab_overview:
    render_overview_tab(filtered_journeys, filtered_touchpoints, filtered_deals)

with tab_journeys:
    render_journeys_tab(filtered_journeys, filtered_touchpoints)

with tab_sla:
    render_sla_velocity_tab(filtered_journeys, filtered_deals)

with tab_scenario:
    render_scenario_tab(filtered_journeys, filtered_touchpoints)

with tab_recs:
    render_recommendations_tab()

with tab_methodology:
    render_methodology_tab()

with tab_data:
    render_data_tab(filtered_touchpoints, filtered_journeys, filtered_deals, df_campaign_costs_raw)
