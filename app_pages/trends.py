"""Trends & predictive analytics — Stitch screen 4."""

import streamlit as st
import pandas as pd

from modules.visualization import Visualization
from ui.components import kpi_card, page_hero, require_data
from utils.helpers import get_sla_threshold


page_hero(
    "Trends & predictive analytics",
    "Historical complaint volume, resolution performance, and SLA breach risk forecasting.",
)

df = require_data()
if df is None:
    st.stop()

viz = Visualization()

with st.container(horizontal=True):
    current_vol = len(df)
    open_vol = int(df["status"].astype(str).str.lower().eq("open").sum()) if "status" in df.columns else 0
    projected = int(open_vol * 1.12) if open_vol else current_vol
    st.markdown(kpi_card("Current volume", f"{current_vol:,}", "Records in dataset"), unsafe_allow_html=True)
    st.markdown(kpi_card("Open queue", f"{open_vol:,}", "Requires attention"), unsafe_allow_html=True)
    st.markdown(kpi_card("Projected load", f"{projected:,}", "Estimated next-period volume"), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.subheader("Resolution time trend")
        if "resolution_time_hours" in df.columns:
            fig = viz.create_resolution_time_trend(df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Parse dates in Settings → Data pipeline to enable this chart.")

with col2:
    with st.container(border=True):
        st.subheader("Ward comparison")
        if "resolution_time_hours" in df.columns and "ward_name" in df.columns:
            fig = viz.create_ward_comparison_chart(df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Resolution hours and ward data required.")

with st.container(border=True):
    st.subheader("Category breakdown")
    fig_cat = viz.create_category_breakdown_chart(df)
    st.plotly_chart(fig_cat, use_container_width=True)

st.divider()
st.subheader("SLA breach prediction")

with st.expander("SLA thresholds reference"):
    sla_data = {
        cat: f"{hrs}h ({hrs // 24}d)"
        for cat, hrs in [
            ("pothole", 168), ("streetlight", 72), ("garbage", 24),
            ("water_leakage", 48), ("drainage", 96),
        ]
    }
    st.table(pd.DataFrame.from_dict(sla_data, orient="index", columns=["Threshold"]))

if st.button("Train SLA prediction model", type="primary", key="trends_train_sla"):
    from modules.sla_prediction import SLAPredictor

    with st.spinner("Training Random Forest classifier…"):
        predictor = SLAPredictor()
        try:
            metrics = predictor.train(df)
            st.session_state.sla_predictor = predictor
            st.session_state.current_step = max(st.session_state.current_step, 5)
            st.success("Model trained successfully.")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Accuracy", f"{metrics['accuracy']:.2%}")
            c2.metric("Precision", f"{metrics['precision']:.2%}")
            c3.metric("Recall", f"{metrics['recall']:.2%}")
            c4.metric("F1 score", f"{metrics['f1']:.2%}")
        except Exception as exc:
            st.error(f"Training failed: {exc}")

if st.session_state.sla_predictor is not None and st.session_state.sla_predictor.is_trained:
    if st.button("Predict breach risk", type="primary", key="trends_predict"):
        predictor = st.session_state.sla_predictor
        try:
            predictions = predictor.predict_breach_risk(df)
            if predictions.empty:
                st.info("No open complaints to predict.")
            else:
                predictions["priority_action"] = predictions.apply(
                    predictor.generate_priority_action, axis=1
                )
                st.session_state.prediction_results = predictions
                high = (predictions["breach_flag"] == "High Risk").sum()
                med = (predictions["breach_flag"] == "Medium Risk").sum()
                low = (predictions["breach_flag"] == "Low Risk").sum()
                m1, m2, m3 = st.columns(3)
                m1.metric("High risk", high)
                m2.metric("Medium risk", med)
                m3.metric("Low risk", low)
                st.dataframe(
                    predictions[[
                        "complaint_id", "category", "ward_name",
                        "breach_probability", "breach_flag", "priority_action",
                    ]].style.format({"breach_probability": "{:.2%}"}),
                    use_container_width=True,
                    hide_index=True,
                )
        except Exception as exc:
            st.error(f"Prediction error: {exc}")

with st.container(border=True):
    st.subheader("SLA breach distribution")
    chart_df = df.copy()
    if "sla_breached" not in chart_df.columns and "resolution_time_hours" in chart_df.columns:
        chart_df["sla_breached"] = chart_df.apply(
            lambda r: (
                1
                if pd.notna(r.get("resolution_time_hours"))
                and r["resolution_time_hours"] > get_sla_threshold(r.get("category", ""))
                else 0
            )
            if r.get("status") == "Resolved"
            else None,
            axis=1,
        )
        chart_df = chart_df.dropna(subset=["sla_breached"])
        chart_df["sla_breached"] = chart_df["sla_breached"].astype(int)
    if "sla_breached" in chart_df.columns:
        fig_sla = viz.create_sla_breach_distribution(chart_df)
        st.plotly_chart(fig_sla, use_container_width=True)
    else:
        st.caption("Train the SLA model or parse resolution dates to view breach distribution.")
