import os

import pandas as pd
import plotly.express as px
import streamlit as st
from db import run_query

st.set_page_config(page_title="Strange Places Dashboard", layout="wide")

PAGES = {
    "Overview": "overview",
    "Geo Heatmap": "heatmap",
    "Time Trends": "trends",
    "Region Comparison": "regions",
}

page = st.sidebar.radio("Navigate", list(PAGES.keys()))


# --------------- Overview ---------------
if page == "Overview":
    st.title("Strange Places Analytics Dashboard")
    st.markdown("Unified view of natural risks and anomalous phenomena across the globe.")

    df = run_query("""
        select
            c.category_name,
            c.category_group,
            c.source_authority,
            count(*) as event_count
        from dbt_ds.ds_fct_events f
        join dbt_ds.ds_dim_category c on f.category_id = c.category_id
        group by c.category_name, c.category_group, c.source_authority
        order by event_count desc
    """)

    grouped = df.groupby("category_group", as_index=False)["event_count"].sum().sort_values("event_count", ascending=False)

    fig = px.bar(grouped, x="category_group", y="event_count", title="Events by Category Group")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Category Breakdown")
    st.dataframe(df, use_container_width=True, hide_index=True)


# --------------- Geo Heatmap ---------------
elif page == "Geo Heatmap":
    st.title("Geo Heatmap")
    st.markdown("Event density aggregated by ~20 km grid cells.")

    df = run_query("""
        select geo_hash, latitude, longitude, category_group, event_count
        from dbt_marts.marts_geo_heatmap
        where event_count > 0
    """)

    groups = ["All Groups"] + sorted(df["category_group"].dropna().unique().tolist())
    selected = st.selectbox("Category Group", groups)

    filtered = df if selected == "All Groups" else df[df["category_group"] == selected]

    fig = px.scatter_map(
        filtered,
        lat="latitude",
        lon="longitude",
        size="event_count",
        color="category_group",
        title="Phenomena Density Map",
        zoom=1,
        height=600,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Cells by Event Count")
    top = df.sort_values("event_count", ascending=False).head(20)
    st.dataframe(top, use_container_width=True, hide_index=True)


# --------------- Time Trends ---------------
elif page == "Time Trends":
    st.title("Time Trends")
    st.markdown("Seasonality and year-over-year dynamics of recorded phenomena.")

    df = run_query("""
        select year, month, season, category_name, category_group,
               event_count, yoy_change_pct
        from dbt_marts.marts_time_trends
    """)

    categories = ["All Categories"] + sorted(df["category_name"].dropna().unique().tolist())
    selected = st.selectbox("Category", categories)

    filt = df if selected == "All Categories" else df[df["category_name"] == selected]

    st.subheader("Annual Event Volume")
    yearly = filt[filt["year"] >= 1950].groupby(["year", "category_group"], as_index=False)["event_count"].sum()
    fig = px.line(yearly, x="year", y="event_count", color="category_group", title="Events per Year")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Seasonality")
    season_order = {"winter": 1, "spring": 2, "summer": 3, "autumn": 4}
    seasonal = filt.groupby(["season", "category_group"], as_index=False)["event_count"].sum()
    seasonal["sort_key"] = seasonal["season"].map(season_order)
    seasonal = seasonal.sort_values("sort_key")
    fig2 = px.bar(seasonal, x="season", y="event_count", color="category_group",
                  barmode="group", title="Events by Season")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Year-over-Year Change")
    yoy = filt[(filt["yoy_change_pct"].notna()) & (filt["year"] >= 2000)].sort_values(
        ["year", "category_name"], ascending=[False, True]
    ).head(100)
    st.dataframe(
        yoy[["year", "category_name", "event_count", "yoy_change_pct"]],
        use_container_width=True,
        hide_index=True,
    )


# --------------- Region Comparison ---------------
elif page == "Region Comparison":
    st.title("Region Comparison")
    st.markdown("Side-by-side comparison of regions: risk index vs. tourism index.")

    df = run_query("""
        select region, total_count, hazard_count, landmark_count,
               anomaly_count, risk_index, tourism_index
        from dbt_marts.marts_region_comparison
        where total_count >= 10
        order by total_count desc
    """)

    st.subheader("Risk vs. Tourism")
    fig = px.scatter(
        df,
        x="risk_index",
        y="tourism_index",
        size="total_count",
        hover_name="region",
        title="Risk Index vs. Tourism Index by Region",
        labels={"risk_index": "Risk Index (%)", "tourism_index": "Tourism Index (%)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Regions by Event Count")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Regions by Risk Level")
    df["risk_level"] = df["risk_index"].apply(
        lambda r: "High Risk (>50%)" if r > 50 else ("Medium Risk (20-50%)" if r > 20 else "Low Risk (<20%)")
    )
    dist = df.groupby("risk_level", as_index=False).agg(
        region_count=("region", "count"),
        total_events=("total_count", "sum"),
    )
    fig2 = px.bar(dist, x="risk_level", y="region_count", title="Regions by Risk Level")
    st.plotly_chart(fig2, use_container_width=True)
