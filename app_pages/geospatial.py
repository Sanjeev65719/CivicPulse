"""Geospatial analysis map — Stitch screen 2."""

import streamlit as st

from modules.visualization import Visualization
from ui.components import page_hero, require_data


page_hero(
    "Geospatial analysis",
    "Explore complaint density, hotspot clusters, and ward-level spatial patterns.",
)

df = require_data()
if df is None:
    st.stop()

with st.container(border=True):
    st.subheader("Layers & controls")
    c1, c2, c3 = st.columns(3)
    categories = sorted(df["category"].dropna().unique()) if "category" in df.columns else []
    wards = sorted(df["ward_name"].dropna().unique()) if "ward_name" in df.columns else []
    selected_categories = c1.multiselect("Complaint types", categories, default=categories, key="geo_categories")
    selected_wards = c2.multiselect("Wards", wards, default=wards, key="geo_wards")
    show_heatmap = c3.toggle("Heatmap overlay", value=True, key="geo_heatmap")

filtered = df.copy()
if "category" in filtered.columns and selected_categories:
    filtered = filtered[filtered["category"].isin(selected_categories)]
if "ward_name" in filtered.columns and selected_wards:
    filtered = filtered[filtered["ward_name"].isin(selected_wards)]

st.divider()

col_left, col_right = st.columns((1.6, 1))
with col_left:
    with st.container(border=True):
        st.subheader("Complaint density map")
        viz = Visualization()
        if show_heatmap and st.session_state.hotspot_results is not None:
            fig = viz.create_hotspot_map(st.session_state.hotspot_results["clustered_df"])
        else:
            fig = viz.create_hotspot_map(filtered)
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    with st.container(border=True):
        st.subheader("Hotspot detection")
        st.caption("Configure DBSCAN to identify geographic clusters.")
        eps_km = st.slider("Radius (km)", 0.1, 5.0, 0.5, 0.1, key="geo_eps")
        min_samples = st.slider("Min samples", 2, 20, 5, 1, key="geo_min_samples")
        if st.button("Run hotspot detection", type="primary", key="geo_run"):
            from modules.hotspot_detection import HotspotDetector

            with st.spinner("Running DBSCAN clustering…"):
                detector = HotspotDetector(eps_km=eps_km, min_samples=min_samples)
                clustered = detector.detect_hotspots(filtered)
                summary = detector.summarize_hotspots(clustered)
                ranked = detector.rank_hotspots_by_severity(summary)
                st.session_state.hotspot_detector = detector
                st.session_state.hotspot_results = {
                    "clustered_df": clustered,
                    "summary": summary,
                    "ranked": ranked,
                }
                st.session_state.current_step = max(st.session_state.current_step, 4)
            st.success("Hotspot analysis complete.")

    if st.session_state.hotspot_results is not None:
        ranked = st.session_state.hotspot_results["ranked"]
        if not ranked.empty:
            with st.container(border=True):
                st.subheader("Top hotspots")
                st.dataframe(
                    ranked.head(5).style.format({
                        "centroid_lat": "{:.4f}",
                        "centroid_lon": "{:.4f}",
                        "avg_resolution_time": "{:.1f}h",
                        "severity_score": "{:.3f}",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )
