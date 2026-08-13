"""Executive overview dashboard — Stitch screen 1."""

import streamlit as st
import pandas as pd

from ui.components import (
    empty_state,
    kpi_card,
    page_hero,
    require_data,
    status_badge,
    working_dataframe,
)


def _avg_resolution_days(df: pd.DataFrame) -> str:
    if "resolution_time_hours" not in df.columns:
        return "—"
    hours = df["resolution_time_hours"].dropna()
    if hours.empty:
        return "—"
    return f"{hours.mean() / 24:.1f} days"


page_hero(
    "Executive overview",
    "Real-time municipal complaint performance, demand signals, and operational priorities.",
)

df = working_dataframe()
if df is None:
    empty_state(
        "Ready to monitor civic operations",
        "Load a complaint dataset to unlock live KPIs, category demand, and priority queues.",
    )
    st.stop()

status = df["status"].astype(str).str.lower() if "status" in df.columns else pd.Series("", index=df.index)
open_count = int(status.isin(["open", "in progress", "pending"]).sum())
resolved_count = int(status.str.contains("resolved|closed", regex=True).sum())
total = len(df)
breached = int(df["sla_breached"].fillna(0).astype(bool).sum()) if "sla_breached" in df.columns else 0
avg_resolution = _avg_resolution_days(df)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(kpi_card("Total complaints", f"{total:,}", "All records in current dataset"), unsafe_allow_html=True)
with c2:
    st.markdown(
        kpi_card("Open vs closed", f"{open_count:,} / {resolved_count:,}", "Active queue vs resolved"),
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(kpi_card("Avg resolution time", avg_resolution, "Based on parsed resolution hours"), unsafe_allow_html=True)

st.markdown('<div class="section-label">Operational analytics</div>', unsafe_allow_html=True)
left, right = st.columns((1.35, 1))

with left:
    with st.container(border=True):
        st.subheader("Complaints by category")
        if "category" in df.columns:
            category_view = df["category"].value_counts().reset_index()
            category_view.columns = ["Category", "Complaints"]
            st.bar_chart(category_view, x="Category", y="Complaints", color="#2563eb")
        else:
            st.caption("Category column required for this chart.")

with right:
    with st.container(border=True):
        st.subheader("Volume over last 30 days")
        if "complaint_date" in df.columns:
            dates = pd.to_datetime(df["complaint_date"], errors="coerce").dropna()
            if not dates.empty:
                daily = dates.dt.date.value_counts().sort_index().reset_index()
                daily.columns = ["Date", "Volume"]
                st.line_chart(daily, x="Date", y="Volume", color="#2563eb")
            else:
                st.caption("No valid complaint dates found.")
        else:
            st.caption("Complaint date column required for trend chart.")

st.markdown('<div class="section-label">High priority issues</div>', unsafe_allow_html=True)
with st.container(border=True):
    cols = [c for c in ["complaint_id", "category", "ward_name", "status", "complaint_date"] if c in df.columns]
    if cols:
        priority_df = df.copy()
        if "status" in priority_df.columns:
            priority_df = priority_df[priority_df["status"].astype(str).str.lower().isin(["open", "in progress", "pending"])]
        display = priority_df[cols].head(8).copy()
        if "status" in display.columns:
            display["status"] = display["status"].apply(lambda s: status_badge(s))
        st.markdown(display.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.caption("No complaint records to display.")

if breached:
    st.warning(f"{breached:,} confirmed SLA breaches detected in the current dataset.")
