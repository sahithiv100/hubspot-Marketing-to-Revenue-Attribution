"""
"How the Algorithm Works" & Methodology Tab.
Explains the full computational pipeline, data flow architecture, mathematical attribution formulas,
value-at-risk calculations, and explicit methodological limitations & disclosures.
"""

import streamlit as st

def render_methodology_tab():
    st.markdown("### 🔬 How the Attribution & Value Leak Algorithm Works")
    st.markdown(
        "A transparent, mathematically grounded overview of the data engineering pipeline, attribution weighting logic, "
        "and funnel value leak calculations powering this application."
    )

    # Connected Architecture Diagram
    st.markdown("#### 1. End-to-End Pipeline Architecture Flow")
    st.markdown("""
```
 ┌──────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
 │  Touchpoint Tracker  │ ───> │  Journey Assembler      │ ───> │  Funnel Stage Mapper    │
 │  • Ad impressions    │      │  • Multi-touch sequence │      │  • Lead -> MQL -> SQL   │
 │  • Website sessions  │      │  • Account resolution   │      │  • Opportunity -> Won   │
 │  • Form submissions  │      │  • Channel costs ($)    │      │  • SDR SLA timestamps   │
 └──────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
                                                                             │
                                                                             ▼
 ┌──────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
 │  Strategic Actions   │ <─── │  Value Leak Calculator  │ <─── │  Attribution Engine     │
 │  • SLA routing       │      │  • Stage drop-off rate  │      │  • First-Touch (FTA)    │
 │  • Budget rebalance  │      │  • Downstream value ($) │      │  • Last-Touch (LTA)     │
 │  • CRO experiments   │      │  • Friction ranking     │      │  • U-Shaped & Linear    │
 └──────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```
    """)

    # Numbered Computational Flow
    st.markdown("#### 2. Computational Step-by-Step Methodology")
    st.markdown("""
1. **Multi-Touch Sequence Reconstruction**:
   Each synthetic prospective account is assigned a persistent identifier (`journey_id`). Individual marketing interactions (`touchpoint_id`) are ordered chronologically:
   $$\\mathcal{T}_k = \\{t_1, t_2, \\dots, t_N\\}$$

2. **Stage Progression & Drop-off Calculus**:
   At each transition from stage $S_i$ to $S_{i+1}$, conversion and drop-off are evaluated:
   $$\\text{CVR}_{i \\to i+1} = \\frac{N_{i+1}}{N_i}, \\quad \\text{Drop-off Rate} = 1 - \\text{CVR}_{i \\to i+1}$$

3. **Funnel Value Leak Realization Formula**:
   When prospective accounts abandon at stage $S_i$, the pipeline value lost is the product of dropped accounts and the downstream expected realization value:
   $$\\text{Value Lost}(S_i) = \\big(N_i - N_{i+1}\\big) \\times P(\\text{Closed Won} \\mid S_i) \\times \\overline{\\text{ACV}}$$
   This ranks friction points by true bottom-line revenue destruction rather than just raw volume percentages.

4. **Multi-Touch Attribution Allocation Formulas**:
   Let a journey have $N$ touchpoints and realized ARR $R$:
   - **First-Touch Attribution (FTA)**:
     $$w_1 = 1.0, \\quad w_i = 0 \\quad (\\forall i > 1)$$
     *Primary purpose*: Measures brand awareness and discovery channel reach.
   - **Last-Touch Attribution (LTA)**:
     $$w_N = 1.0, \\quad w_i = 0 \\quad (\\forall i < N)$$
     *Primary purpose*: Measures bottom-of-funnel conversion catalyst efficiency.
   - **Linear Attribution (MTA)**:
     $$w_i = \\frac{1}{N} \\quad (\\forall i \\in [1, N])$$
     *Primary purpose*: Equalized contribution across all journey touches.
   - **U-Shaped (Position-Based) Attribution**:
     $$w_1 = 0.40, \\quad w_N = 0.40, \\quad w_i = \\frac{0.20}{N - 2} \\quad (\\text{for } 1 < i < N, \\, N \\ge 3)$$
     *Primary purpose*: Recognizes that first discovery and final conversion are the most critical milestones.
   - **Time-Decay Attribution**:
     $$w_i = \\frac{2^{-(t_N - t_i)/\\lambda}}{\\sum_{j=1}^N 2^{-(t_N - t_j)/\\lambda}}$$
     where $\\lambda = 14\\text{ days}$ half-life.
    """)

    # Limitations & Governance
    st.markdown("#### 3. Methodological Limitations & Governance Disclosures")
    st.markdown("""
> [!WARNING]
> **Attribution Models Are Not Causal Proofs**:
> Rule-based attribution models (First-Touch, Last-Touch, Linear, U-Shaped) are heuristic accounting mechanisms. They describe correlation along observed customer journeys, not incremental causal lift.

- **Absence of Counterfactual Baseline**: A channel with high Last-Touch revenue (e.g. Branded Paid Search) often intercepts buyers who were already determined to purchase. Eliminating it might not reduce sales by the full attributed amount.
- **Unobserved Touchpoints**: Offline conversations, peer word-of-mouth, podcast listening, and executive referrals cannot always be tracked deterministically.
- **Incrementality Validation Requirement**: Any decision to cut or double a marketing channel's budget should be validated with geo-matched holdout tests or randomized conversion lift studies before permanent implementation.
    """)
