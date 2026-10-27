"""
Data Explorer, Data Dictionary & Raw Export Tab.
Provides interactive filters, paginated table previews, data dictionaries, and downloadable CSV exports.
"""

import streamlit as st
import pandas as pd

def render_data_tab(df_touchpoints: pd.DataFrame, df_journeys: pd.DataFrame, df_deals: pd.DataFrame, df_campaign_costs: pd.DataFrame):
    st.markdown("### 🗃️ Data Explorer, Dictionary & Raw Exports")
    st.markdown(
        "Inspect, filter, and export the synthetic datasets powering the HubSpot attribution prototype. "
        "All records are strictly synthetic and generated in-memory."
    )

    data_view = st.radio(
        "Select Dataset to Inspect",
        ["Customer Journeys", "Marketing Touchpoints", "Sales Deals & Pipeline", "Campaign Spend Summary", "Data Dictionary"],
        horizontal=True
    )

    if data_view == "Customer Journeys":
        st.markdown("#### Prospective Customer Journeys Table")
        st.caption(f"Total Records: {len(df_journeys):,}")

        # Quick filters
        c1, c2, c3 = st.columns(3)
        with c1:
            size_filter = st.multiselect("Company Size", df_journeys["company_size"].unique(), default=df_journeys["company_size"].unique())
        with c2:
            stage_filter = st.multiselect("Final Stage", df_journeys["final_stage"].unique(), default=df_journeys["final_stage"].unique())
        with c3:
            region_filter = st.multiselect("Region", df_journeys["region"].unique(), default=df_journeys["region"].unique())

        filtered = df_journeys[
            df_journeys["company_size"].isin(size_filter) &
            df_journeys["final_stage"].isin(stage_filter) &
            df_journeys["region"].isin(region_filter)
        ]

        st.dataframe(filtered.head(200), use_container_width=True)

        csv_journeys = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Journeys (CSV)",
            data=csv_journeys,
            file_name="hubspot_synthetic_customer_journeys.csv",
            mime="text/csv"
        )

    elif data_view == "Marketing Touchpoints":
        st.markdown("#### Multi-Touch Marketing Touchpoints Table")
        st.caption(f"Total Records: {len(df_touchpoints):,}")

        ch_filter = st.multiselect("Filter by Channel", df_touchpoints["channel"].unique(), default=df_touchpoints["channel"].unique())
        filtered_tp = df_touchpoints[df_touchpoints["channel"].isin(ch_filter)]

        st.dataframe(filtered_tp.head(200), use_container_width=True)

        csv_tp = filtered_tp.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Touchpoints (CSV)",
            data=csv_tp,
            file_name="hubspot_synthetic_touchpoints.csv",
            mime="text/csv"
        )

    elif data_view == "Sales Deals & Pipeline":
        st.markdown("#### Sales Opportunities & Closed ARR Table")
        st.caption(f"Total Records: {len(df_deals):,}")

        if not df_deals.empty:
            prod_filter = st.multiselect("Filter Product Hub", df_deals["hub_product"].unique(), default=df_deals["hub_product"].unique())
            filtered_deals = df_deals[df_deals["hub_product"].isin(prod_filter)]
            st.dataframe(filtered_deals.head(200), use_container_width=True)

            csv_deals = filtered_deals.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Filtered Deals (CSV)",
                data=csv_deals,
                file_name="hubspot_synthetic_sales_deals.csv",
                mime="text/csv"
            )
        else:
            st.info("No deal records generated.")

    elif data_view == "Campaign Spend Summary":
        st.markdown("#### Aggregated Campaign Spend & Volume Summary")
        st.dataframe(df_campaign_costs, use_container_width=True)

        csv_camps = df_campaign_costs.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Campaign Costs (CSV)",
            data=csv_camps,
            file_name="hubspot_synthetic_campaign_costs.csv",
            mime="text/csv"
        )

    elif data_view == "Data Dictionary":
        st.markdown("#### 📖 Comprehensive Data Dictionary")
        dict_data = [
            {"Dataset": "Journeys", "Column": "journey_id", "Type": "String", "Description": "Unique identifier for synthetic prospect account journey."},
            {"Dataset": "Journeys", "Column": "company_name", "Type": "String", "Description": "Fictional company name."},
            {"Dataset": "Journeys", "Column": "industry", "Type": "String", "Description": "Business sector (e.g. B2B SaaS, FinTech, Healthcare)."},
            {"Dataset": "Journeys", "Column": "lead_score", "Type": "Integer", "Description": "Predictive ICP fit score (1 to 100)."},
            {"Dataset": "Journeys", "Column": "sdr_response_hours", "Type": "Float", "Description": "Elapsed time from MQL form submission to first SDR outreach."},
            {"Dataset": "Journeys", "Column": "closed_revenue", "Type": "Float", "Description": "Realized Annual Contract Value (ARR) for won deals."},
            {"Dataset": "Touchpoints", "Column": "touchpoint_id", "Type": "String", "Description": "Unique identifier for individual marketing touchpoint."},
            {"Dataset": "Touchpoints", "Column": "channel", "Type": "String", "Description": "Marketing channel (e.g. Paid Search, LinkedIn, SEO)."},
            {"Dataset": "Touchpoints", "Column": "campaign_name", "Type": "String", "Description": "Marketing campaign attribution tag."},
            {"Dataset": "Touchpoints", "Column": "cost", "Type": "Float", "Description": "Synthetic marginal ad spend / engagement cost ($)."},
            {"Dataset": "Touchpoints", "Column": "stage_at_touch", "Type": "String", "Description": "Funnel stage when interaction occurred."},
            {"Dataset": "Deals", "Column": "deal_id", "Type": "String", "Description": "CRM Opportunity identifier."},
            {"Dataset": "Deals", "Column": "hub_product", "Type": "String", "Description": "HubSpot product tier (Marketing Hub, Sales Hub, CRM Suite)."},
            {"Dataset": "Deals", "Column": "deal_value", "Type": "Float", "Description": "Proposed or closed contract ARR ($)."},
            {"Dataset": "Deals", "Column": "sales_cycle_days", "Type": "Integer", "Description": "Days elapsed from Opportunity creation to close date."}
        ]
        df_dict = pd.DataFrame(dict_data)
        st.dataframe(df_dict, use_container_width=True, hide_index=True)

        csv_dict = df_dict.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Data Dictionary (CSV)",
            data=csv_dict,
            file_name="hubspot_attribution_data_dictionary.csv",
            mime="text/csv"
        )
