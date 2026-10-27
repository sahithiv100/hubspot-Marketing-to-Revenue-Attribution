# HubSpot Marketing-to-Revenue Attribution & Funnel Value Leak Detector

> **DISCLAIMER:**  
> **SYNTHETIC DEMO DATA — NOT REAL COMPANY DATA.**  
> This project is an illustrative prototype developed for analytical and demonstration purposes. All account names, touchpoints, conversion rates, deal sizes, and metrics are synthetic. It does not scrape HubSpot or represent actual internal confidential systems.

---

## 🎯 Business Problem & Objective
In modern B2B SaaS marketing, customer journeys are multi-touch, non-linear, and span across months. B2B revenue teams often suffer from two critical blindspots:
1. **Misleading Single-Touch Attribution:** Relying strictly on Last-Touch attribution attributes 100% of pipeline credit to bottom-of-funnel actions (e.g., direct demo requests or branded search), obscuring the massive role top-of-funnel content marketing and SEO play in initial discovery.
2. **Invisible Funnel Value Leaks:** High drop-off between Marketing Qualified Leads (MQL) and Sales Qualified Leads (SQL) frequently destroys millions in pipeline value due to slow sales response times (SLA breaches), rather than poor marketing lead quality.

This application traces synthetic customer journeys from initial marketing exposure (Paid Search, Paid Social, Organic Search, Content/Blog, Webinars, Email) to closed ARR, compares 5 attribution lenses, locates and ranks dollar-denominated funnel leaks, and provides interactive what-if scenario simulations.

---

## 📂 Project Architecture

```
hubspot-marketing-attribution/
├── app.py                      # Main Streamlit web application & sidebar controls
├── requirements.txt            # Python package dependencies
├── README.md                   # Complete documentation and setup guide
├── test_pipeline.py            # Backend logic self-test suite
├── test_ui.py                  # Chart rendering validation test
├── data/
│   ├── __init__.py
│   └── synthetic_generator.py  # Fictional B2B journey, touchpoint, and deal generator
├── models/
│   ├── __init__.py
│   ├── attribution.py          # First-Touch, Last-Touch, Linear, U-Shaped, Time-Decay MTA
│   ├── funnel_analysis.py      # Funnel CVR, unit economics, value leaks, SDR SLA velocity
│   └── scenario_simulator.py   # Dynamic What-If budget reallocation and SLA simulator
└── ui/
    ├── __init__.py
    ├── components.py           # Dark navy theme CSS, KPI cards, manager callouts, banners
    ├── charts.py               # Plotly interactive visualizations (funnels, heatmaps, bubbles)
    └── tabs/
        ├── __init__.py
        ├── overview_tab.py     # Executive funnel, leak detector, drop-off heatmap, Manager Q1
        ├── journeys_tab.py     # Individual journey explorer, MTA comparison, Manager Q2
        ├── sla_velocity_tab.py # Inbound SDR response SLA decay & lead fit scores, Manager Q3
        ├── scenario_tab.py     # What-If growth optimizer & dynamic recalculation
        ├── recommendations_tab.py # Ranked interventions, assumptions, impact, human review
        ├── methodology_tab.py  # Pipeline flowchart, formulas, limitations & disclosure
        └── data_tab.py         # Data explorer, data dictionary, real CSV downloads
```

---

## 💡 Manager Questions Explored

1. **Manager Question 1: Where is our biggest drop-off and revenue leak in the funnel?**
   - **Answer:** The **MQL $\to$ SQL transition** leaks the highest downstream dollar value ($230k+ - $850k+ in pipeline ARR depending on sample size). Even though top-of-funnel Lead $\to$ MQL has high drop-off percentage, MQLs carry a far higher downstream realization probability.
2. **Manager Question 2: Which channel looks best on First-Touch vs Multi-Touch, and which one would be mistakenly cut?**
   - **Answer:** **Content Marketing / Blog** and **Organic Search (SEO)** generate up to **3.8x more revenue credit** under First-Touch and U-Shaped models than under Last-Touch. A naive executive using Last-Touch would defund the blog, choking future inbound pipeline.
3. **Manager Question 3: How does SDR response time impact conversion and revenue?**
   - **Answer:** Inbound leads contacted in **$< 1$ hour convert at 48%**, delivering a **$5.2\times$ higher revenue yield per MQL** compared to leads delayed beyond 24 hours (8% conversion). Reducing response lag is the highest-ROI RevOps lever.

---

## 🔬 Mathematical Formulations

### 1. Funnel Value-at-Risk
$$\text{Value Lost}(S_i) = \big(N_i - N_{i+1}\big) \times P(\text{Closed Won} \mid S_i) \times \overline{\text{ACV}}$$

### 2. Multi-Touch Attribution Weighting
- **First-Touch Attribution (FTA):** $w_1 = 1.0, \, w_i = 0 \, (\forall i > 1)$
- **Last-Touch Attribution (LTA):** $w_N = 1.0, \, w_i = 0 \, (\forall i < N)$
- **Linear Attribution:** $w_i = \frac{1}{N} \, (\forall i \in [1, N])$
- **U-Shaped (Position-Based):** $w_1 = 0.40, \, w_N = 0.40, \, w_i = \frac{0.20}{N - 2} \, (1 < i < N)$
- **Time-Decay:** $w_i = \frac{2^{-(t_N - t_i)/\lambda}}{\sum_j 2^{-(t_N - t_j)/\lambda}}$ with $\lambda = 14\text{ days}$.

> **Governance Notice:** Attribution weights are heuristic accounting allocations of observed journeys, **not causal proof of counterfactual lift**. High-impact budget reallocations require controlled holdout/geo-incrementality testing and human executive review.

---

## 🚀 Windows-Friendly Launch Instructions

### Prerequisites
- Python 3.10+ installed on Windows (e.g., standard Python or Anaconda).
- PowerShell or Windows Command Prompt.

### Step 1: Open PowerShell and Navigate to the Project
```powershell
cd C:\Users\DELL\.gemini\antigravity\scratch\hubspot-marketing-attribution
```

*(Recommended: Set this folder as your active workspace in your IDE).*

### Step 2: Create and Activate a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first).*

### Step 3: Install Required Packages
```powershell
pip install -r requirements.txt
```

### Step 4: Run Backend Test Suite
```powershell
python test_pipeline.py
python test_ui.py
```

### Step 5: Launch the Interactive Web Application
```powershell
streamlit run app.py
```
Streamlit will automatically open your browser at `http://localhost:8501`.

---

## 🎨 Design & Accessibility
- **Color Palette:** Dark navy/charcoal background (`#0E1117`, `#161B26`), borders (`#232D42`), and restrained purple accents (`#8B5CF6`, `#A78BFA`, `#6366F1`).
- **Interactive Controls:** Dynamic seed selector, sample size slider, channel/region/size multiselect filters, what-if scenario sliders, and real CSV file downloads for all datasets.
- **Human-in-the-Loop:** Explicit governance badges signifying that high-impact automated recommendations require human executive authorization.
