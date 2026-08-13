"""Complaint explorer table — Stitch screen 3."""

import streamlit as st
import pandas as pd

from ui.components import enrich_complaints, page_hero, require_data, status_badge


page_hero(
    "Complaint explorer",
    "Search, filter, and review municipal complaints with status and priority indicators.",
)

df = require_data()
if df is None:
    st.stop()

enriched = enrich_complaints(df)

with st.container(border=True):
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    search = f1.text_input("Search", placeholder="ID, ward, description…", key="explorer_search")
    categories = sorted(enriched["category"].dropna().unique()) if "category" in enriched.columns else []
    statuses = sorted(enriched["status"].dropna().unique()) if "status" in enriched.columns else []
    cat_filter = f2.multiselect("Category", categories, default=categories, key="explorer_cat")
    status_filter = f3.multiselect("Status", statuses, default=statuses, key="explorer_status")
    page_size = f4.selectbox("Rows per page", [10, 25, 50, 100], index=1, key="explorer_page_size")
    st.markdown("</div>", unsafe_allow_html=True)

filtered = enriched.copy()
if "category" in filtered.columns and cat_filter:
    filtered = filtered[filtered["category"].isin(cat_filter)]
if "status" in filtered.columns and status_filter:
    filtered = filtered[filtered["status"].isin(status_filter)]
if search:
    mask = pd.Series(False, index=filtered.index)
    for col in ["complaint_id", "ward_name", "description", "category"]:
        if col in filtered.columns:
            mask |= filtered[col].astype(str).str.contains(search, case=False, na=False)
    filtered = filtered[mask]

total_rows = len(filtered)
total_pages = max(1, (total_rows + page_size - 1) // page_size)
if "explorer_page" not in st.session_state:
    st.session_state.explorer_page = 1
page = st.session_state.explorer_page
page = max(1, min(page, total_pages))

nav1, nav2, nav3 = st.columns([1, 2, 1])
with nav1:
    if st.button("Previous", disabled=page <= 1, key="explorer_prev"):
        st.session_state.explorer_page = page - 1
        st.rerun()
with nav2:
    st.caption(f"Showing page {page} of {total_pages} · {total_rows:,} complaints")
with nav3:
    if st.button("Next", disabled=page >= total_pages, key="explorer_next"):
        st.session_state.explorer_page = page + 1
        st.rerun()

start = (page - 1) * page_size
page_df = filtered.iloc[start : start + page_size].copy()

display_cols = [c for c in [
    "complaint_id", "category", "ward_name", "complaint_date", "status", "priority", "description"
] if c in page_df.columns]

if display_cols:
    table = page_df[display_cols].copy()
    if "status" in table.columns:
        table["status"] = table["status"].apply(status_badge)
    st.markdown(table.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.dataframe(page_df, use_container_width=True, hide_index=True)

with st.expander("Bulk actions & export"):
    st.download_button(
        "Download filtered CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="complaints_export.csv",
        mime="text/csv",
        key="explorer_download",
    )
