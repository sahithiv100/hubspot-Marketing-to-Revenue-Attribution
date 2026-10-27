"""
Synthetic Data Generator for HubSpot Marketing-to-Revenue Attribution Prototype.
Generates internally consistent fictional data for:
- Campaign touchpoints and sessions
- Leads, MQLs, SQLs, and CRM stage progressions
- Sales activities and SDR response SLAs
- Opportunities, deal values, close dates, and revenue
- Marketing campaign costs and channel spend

NOTE: ALL DATA GENERATED IS STRICTLY SYNTHETIC AND FOR DEMO / PROTOTYPE PURPOSES ONLY.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_synthetic_data(seed: int = 42, num_journeys: int = 1200):
    """
    Generate synthetic marketing touchpoints, journeys, and deal pipelines.
    Guarantees reproducibility via random seed.
    """
    np.random.seed(seed)
    random.seed(seed)

    company_prefixes = [
        "Acme", "Vanguard", "Apex", "Catalyst", "Zenith", "CloudScale", "Omni", "Starlight",
        "NextGen", "Pulse", "Stratum", "Synergy", "Hyperion", "Beacon", "Cobalt", "Crestline",
        "Terra", "Velocity", "Aura", "Quantum", "PeakFlow", "Lumina", "Elevate", "Horizon"
    ]
    company_suffixes = [
        "Logistics", "Software", "Health", "Fintech", "Media", "Retail", "Security", "Analytics",
        "Bio", "Networks", "Consulting", "Solutions", "Technologies", "Interactive", "Capital"
    ]

    channels = [
        "Paid Search - Brand",
        "Paid Search - NonBrand",
        "Paid Social - LinkedIn",
        "Organic Search (SEO)",
        "Content Marketing / Blog",
        "Webinars & Virtual Events",
        "Email Nurture",
        "Partner & Referral"
    ]

    channel_cost_per_touch = {
        "Paid Search - Brand": 14.50,
        "Paid Search - NonBrand": 38.00,
        "Paid Social - LinkedIn": 52.00,
        "Organic Search (SEO)": 3.20,
        "Content Marketing / Blog": 4.50,
        "Webinars & Virtual Events": 45.00,
        "Email Nurture": 0.85,
        "Partner & Referral": 22.00
    }

    campaign_lookup = {
        "Paid Search - Brand": ["Brand_Search_Exact_US", "Brand_Competitor_Defend_EMEA"],
        "Paid Search - NonBrand": ["CRM_Platform_Keywords_US", "Inbound_Marketing_Software_Search", "RevOps_Tools_HighIntent"],
        "Paid Social - LinkedIn": ["LI_ABM_RevOps_VP_DecisionMakers", "LI_Marketing_Ops_Guide_Sponsored", "LI_Inbound25_Teaser"],
        "Organic Search (SEO)": ["HubSpot_Academy_Organic", "SEO_TopicCluster_CustomerAcquisition", "SEO_Inbound_Methodology_Hub"],
        "Content Marketing / Blog": ["Blog_State_of_Marketing_Report", "Blog_Email_Open_Rate_Benchmarks", "Blog_SaaS_Pricing_Strategy"],
        "Webinars & Virtual Events": ["Webinar_RevOps_Masterclass", "Webinar_AI_Inbound_Playbook", "Virtual_Product_DeepDive_Demo"],
        "Email Nurture": ["Lifecycle_Onboarding_Nurture", "Product_Feature_Spotlight_Email", "ReEngagement_Campaign_Enterprise"],
        "Partner & Referral": ["Solutions_Partner_Referral_Tier1", "App_Marketplace_CoMarketing"]
    }

    hub_products = [
        "Marketing Hub Professional",
        "Marketing Hub Enterprise",
        "Sales Hub Professional",
        "Sales Hub Enterprise",
        "CRM Starter Suite",
        "Full Customer Platform (CRM + Marketing + Sales)"
    ]

    hub_acv_ranges = {
        "CRM Starter Suite": (3600, 7200),
        "Sales Hub Professional": (7200, 14400),
        "Marketing Hub Professional": (10800, 21600),
        "Sales Hub Enterprise": (18000, 36000),
        "Marketing Hub Enterprise": (28000, 54000),
        "Full Customer Platform (CRM + Marketing + Sales)": (45000, 95000)
    }

    industries = ["B2B SaaS", "Financial Services", "Healthcare & Life Sciences", "Professional Services", "E-commerce & Retail", "Manufacturing & Supply Chain"]
    regions = ["North America (NA)", "EMEA", "APAC", "LATAM"]
    company_sizes = ["Startup (1-50)", "Mid-Market (51-500)", "Enterprise (501-5000)"]
    company_size_weights = [0.45, 0.40, 0.15]

    start_date = datetime(2025, 4, 1)

    touchpoints_records = []
    journeys_records = []
    deals_records = []

    for j_idx in range(1, num_journeys + 1):
        journey_id = f"JRN-{10000 + j_idx}"
        company_name = f"{random.choice(company_prefixes)} {random.choice(company_suffixes)}"
        industry = random.choice(industries)
        region = np.random.choice(regions, p=[0.55, 0.25, 0.15, 0.05])
        company_size = np.random.choice(company_sizes, p=company_size_weights)

        # Baseline ICP fit score (1 to 100)
        base_score = np.random.normal(62, 18)
        if company_size == "Enterprise (501-5000)":
            base_score += 12
        elif company_size == "Startup (1-50)":
            base_score -= 5
        lead_score = int(np.clip(base_score, 15, 99))

        # First touch channel selection
        first_channel_probs = [0.18, 0.20, 0.16, 0.22, 0.14, 0.04, 0.01, 0.05]
        first_channel = np.random.choice(channels, p=first_channel_probs)

        # Journey start time
        journey_start_offset = np.random.randint(0, 300)
        current_time = start_date + timedelta(days=journey_start_offset, hours=np.random.randint(8, 18), minutes=np.random.randint(0, 59))

        journey_touchpoints = []

        # 1. First Touchpoint
        t_id_1 = f"TP-{j_idx * 100 + 1}"
        camp_1 = random.choice(campaign_lookup[first_channel])
        cost_1 = channel_cost_per_touch[first_channel] * np.random.uniform(0.85, 1.25)

        tp1 = {
            "touchpoint_id": t_id_1,
            "journey_id": journey_id,
            "company_name": company_name,
            "timestamp": current_time,
            "channel": first_channel,
            "campaign_name": camp_1,
            "touchpoint_type": "First Discovery Exposure",
            "cost": round(cost_1, 2),
            "is_first_touch": True,
            "is_last_touch": False,
            "stage_at_touch": "Lead"
        }
        journey_touchpoints.append(tp1)

        # Progression logic through funnel
        # Stage 1: Lead (Created by definition)
        # Stage 2: MQL Qualification
        # Probability depends on initial channel & lead score
        mql_prob = 0.55 if lead_score >= 60 else 0.28
        if first_channel in ["Organic Search (SEO)", "Content Marketing / Blog"]:
            mql_prob += 0.08
        elif first_channel == "Paid Social - LinkedIn":
            mql_prob += 0.05

        is_mql = np.random.rand() < mql_prob

        # Intermediate touches before MQL
        intermediate_count = np.random.choice([0, 1, 2, 3], p=[0.30, 0.40, 0.20, 0.10])
        for step in range(intermediate_count):
            current_time += timedelta(days=int(np.random.exponential(4) + 1), hours=np.random.randint(1, 8))
            next_ch = np.random.choice(channels, p=[0.12, 0.14, 0.14, 0.20, 0.20, 0.08, 0.10, 0.02])
            next_camp = random.choice(campaign_lookup[next_ch])
            next_cost = channel_cost_per_touch[next_ch] * np.random.uniform(0.85, 1.25)
            tp_inter = {
                "touchpoint_id": f"TP-{j_idx * 100 + len(journey_touchpoints) + 1}",
                "journey_id": journey_id,
                "company_name": company_name,
                "timestamp": current_time,
                "channel": next_ch,
                "campaign_name": next_camp,
                "touchpoint_type": "Nurturing Interaction",
                "cost": round(next_cost, 2),
                "is_first_touch": False,
                "is_last_touch": False,
                "stage_at_touch": "Lead"
            }
            journey_touchpoints.append(tp_inter)

        mql_timestamp = None
        sql_timestamp = None
        opp_timestamp = None
        close_timestamp = None
        disqualification_reason = None
        sdr_response_hours = round(float(np.random.lognormal(mean=2.1, sigma=1.1)), 1) # Median ~8 hrs, long tail up to 72 hrs

        is_sql = False
        is_opp = False
        is_won = False
        product = np.random.choice(hub_products, p=[0.24, 0.16, 0.26, 0.14, 0.12, 0.08])
        acv_min, acv_max = hub_acv_ranges[product]
        deal_value = round(float(np.random.uniform(acv_min, acv_max)), -2)
        lost_reason = None

        if is_mql:
            current_time += timedelta(days=int(np.random.exponential(2) + 1), hours=np.random.randint(1, 5))
            mql_timestamp = current_time

            # MQL conversion touchpoint
            mql_ch = np.random.choice(["Webinars & Virtual Events", "Content Marketing / Blog", "Paid Search - Brand", "Organic Search (SEO)"], p=[0.35, 0.25, 0.25, 0.15])
            tp_mql = {
                "touchpoint_id": f"TP-{j_idx * 100 + len(journey_touchpoints) + 1}",
                "journey_id": journey_id,
                "company_name": company_name,
                "timestamp": current_time,
                "channel": mql_ch,
                "campaign_name": random.choice(campaign_lookup[mql_ch]),
                "touchpoint_type": "MQL Form Submission / Demo Request",
                "cost": round(channel_cost_per_touch[mql_ch] * 1.1, 2),
                "is_first_touch": False,
                "is_last_touch": False,
                "stage_at_touch": "MQL"
            }
            journey_touchpoints.append(tp_mql)

            # Stage 3: MQL to SQL conversion
            # Strongly influenced by SDR SLA Response Time & Lead Score!
            # Under 1 hour: 48% conversion
            # 1 to 4 hours: 35% conversion
            # 4 to 24 hours: 22% conversion
            # > 24 hours: 8% conversion
            if sdr_response_hours <= 1.0:
                sla_sql_rate = 0.48
            elif sdr_response_hours <= 4.0:
                sla_sql_rate = 0.35
            elif sdr_response_hours <= 24.0:
                sla_sql_rate = 0.22
            else:
                sla_sql_rate = 0.08

            # Adjust by lead score fit
            score_factor = lead_score / 60.0
            effective_sql_prob = np.clip(sla_sql_rate * score_factor, 0.03, 0.75)

            is_sql = np.random.rand() < effective_sql_prob

            if is_sql:
                current_time += timedelta(hours=int(sdr_response_hours) + 2, minutes=np.random.randint(10, 50))
                sql_timestamp = current_time

                # SQL Touchpoint: SDR qualification call
                tp_sql = {
                    "touchpoint_id": f"TP-{j_idx * 100 + len(journey_touchpoints) + 1}",
                    "journey_id": journey_id,
                    "company_name": company_name,
                    "timestamp": current_time,
                    "channel": "Email Nurture" if np.random.rand() > 0.4 else "Paid Search - Brand",
                    "campaign_name": "Sales_Cadence_Discovery",
                    "touchpoint_type": "SDR Qualification Call Held",
                    "cost": 15.00,
                    "is_first_touch": False,
                    "is_last_touch": False,
                    "stage_at_touch": "SQL"
                }
                journey_touchpoints.append(tp_sql)

                # Stage 4: SQL to Opportunity
                # BANT qualification & AE Discovery
                opp_prob = 0.62 if company_size != "Startup (1-50)" else 0.48
                is_opp = np.random.rand() < opp_prob

                if is_opp:
                    current_time += timedelta(days=int(np.random.exponential(6) + 3))
                    opp_timestamp = current_time

                    # Mid-funnel touchpoint: AE Demo / Executive Pitch
                    ae_ch = np.random.choice(["Paid Search - Brand", "Webinars & Virtual Events", "Partner & Referral"], p=[0.50, 0.30, 0.20])
                    tp_opp = {
                        "touchpoint_id": f"TP-{j_idx * 100 + len(journey_touchpoints) + 1}",
                        "journey_id": journey_id,
                        "company_name": company_name,
                        "timestamp": current_time,
                        "channel": ae_ch,
                        "campaign_name": random.choice(campaign_lookup[ae_ch]),
                        "touchpoint_type": "AE Product Deep Dive / Proposal Review",
                        "cost": 25.00,
                        "is_first_touch": False,
                        "is_last_touch": False,
                        "stage_at_touch": "Opportunity"
                    }
                    journey_touchpoints.append(tp_opp)

                    # Stage 5: Opportunity to Closed Won
                    # Win rate varies by deal size and number of touches
                    win_prob = 0.32
                    if len(journey_touchpoints) >= 4:
                        win_prob += 0.08
                    if lead_score > 75:
                        win_prob += 0.09
                    if sdr_response_hours > 24.0:
                        win_prob -= 0.06

                    is_won = np.random.rand() < win_prob
                    sales_cycle_days = int(np.random.normal(42, 16))
                    if company_size == "Enterprise (501-5000)":
                        sales_cycle_days += 25
                    sales_cycle_days = max(7, sales_cycle_days)

                    current_time += timedelta(days=sales_cycle_days)
                    close_timestamp = current_time

                    if not is_won:
                        lost_reason = np.random.choice([
                            "Chose Competitor (Salesforce / Dynamics)",
                            "Budget Frozen / Economic Caution",
                            "Champion Departed Company",
                            "Pricing Resistance / Discount Demand",
                            "Feature Gap (Enterprise Security/SSO)"
                        ], p=[0.35, 0.25, 0.15, 0.15, 0.10])
                else:
                    disqualification_reason = "No active budget or project timeline delayed"
            else:
                disqualification_reason = "Unresponsive to SDR or poor ICP fit"
        else:
            disqualification_reason = "Top of funnel bounce / low intent"

        # Final journey stage determination
        if is_won:
            final_stage = "Closed Won"
        elif is_opp:
            final_stage = "Closed Lost"
        elif is_sql:
            final_stage = "Disqualified SQL"
        elif is_mql:
            final_stage = "Unconverted MQL"
        else:
            final_stage = "Unqualified Lead"

        # Mark the last touchpoint
        if journey_touchpoints:
            journey_touchpoints[-1]["is_last_touch"] = True

        total_journey_cost = sum(tp["cost"] for tp in journey_touchpoints)
        journey_duration_days = (journey_touchpoints[-1]["timestamp"] - journey_touchpoints[0]["timestamp"]).days if len(journey_touchpoints) > 1 else 0

        # Build Journey record
        j_rec = {
            "journey_id": journey_id,
            "company_name": company_name,
            "industry": industry,
            "region": region,
            "company_size": company_size,
            "lead_score": lead_score,
            "touchpoint_count": len(journey_touchpoints),
            "first_touch_channel": journey_touchpoints[0]["channel"],
            "last_touch_channel": journey_touchpoints[-1]["channel"],
            "first_touch_date": journey_touchpoints[0]["timestamp"],
            "last_touch_date": journey_touchpoints[-1]["timestamp"],
            "duration_days": journey_duration_days,
            "sdr_response_hours": sdr_response_hours,
            "is_mql": is_mql,
            "is_sql": is_sql,
            "is_opp": is_opp,
            "is_won": is_won,
            "final_stage": final_stage,
            "disqualification_reason": disqualification_reason or lost_reason or "N/A",
            "total_marketing_cost": round(total_journey_cost, 2),
            "closed_revenue": deal_value if is_won else 0.0
        }
        journeys_records.append(j_rec)

        for tp in journey_touchpoints:
            touchpoints_records.append(tp)

        # Build Deal record if reached Opportunity
        if is_opp:
            deal_id = f"DEAL-{20000 + j_idx}"
            deals_records.append({
                "deal_id": deal_id,
                "journey_id": journey_id,
                "company_name": company_name,
                "industry": industry,
                "region": region,
                "company_size": company_size,
                "hub_product": product,
                "deal_value": deal_value,
                "is_won": is_won,
                "stage": "Closed Won" if is_won else "Closed Lost",
                "lost_reason": lost_reason if not is_won else "Won",
                "created_date": opp_timestamp,
                "close_date": close_timestamp,
                "sales_cycle_days": (close_timestamp - opp_timestamp).days if (close_timestamp and opp_timestamp) else 0,
                "first_touch_channel": journey_touchpoints[0]["channel"],
                "last_touch_channel": journey_touchpoints[-1]["channel"]
            })

    df_touchpoints = pd.DataFrame(touchpoints_records)
    df_journeys = pd.DataFrame(journeys_records)
    df_deals = pd.DataFrame(deals_records)

    # Ensure timestamps are actual datetimes
    df_touchpoints["timestamp"] = pd.to_datetime(df_touchpoints["timestamp"])
    df_journeys["first_touch_date"] = pd.to_datetime(df_journeys["first_touch_date"])
    df_journeys["last_touch_date"] = pd.to_datetime(df_journeys["last_touch_date"])
    if not df_deals.empty:
        df_deals["created_date"] = pd.to_datetime(df_deals["created_date"])
        df_deals["close_date"] = pd.to_datetime(df_deals["close_date"])

    # Aggregate Campaign Cost Summary Table
    df_campaign_costs = df_touchpoints.groupby(["channel", "campaign_name"]).agg(
        total_touches=("touchpoint_id", "count"),
        total_cost=("cost", "sum")
    ).reset_index()
    df_campaign_costs["total_cost"] = df_campaign_costs["total_cost"].round(2)

    return df_touchpoints, df_journeys, df_deals, df_campaign_costs
