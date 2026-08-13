"""Manual complaint entry & data ingestion — Stitch screen 5."""

import json

import streamlit as st

from modules.data_ingestion import DataIngestion
from ui.components import page_hero, render_stepper
from ui.state import PROJECT_ROOT
from utils.helpers import format_bytes, validate_file_size


page_hero(
    "New complaint",
    "Submit a manual complaint or import data from files, sample datasets, or APIs.",
)

steps = ["General info", "Details", "Review & submit"]
step = st.session_state.complaint_form_step
render_stepper(steps, step)

ingestion = DataIngestion()

if step == 0:
    with st.container(border=True):
        st.subheader("Data source")
        src_choice = st.radio(
            "How would you like to add complaints?",
            ["Manual entry", "Upload file", "Sample dataset", "API endpoint"],
            horizontal=True,
            key="new_complaint_source",
        )
        st.session_state.ingestion_mode = src_choice

        if src_choice == "Upload file":
            uploaded = st.file_uploader("CSV or XLSX", type=["csv", "xlsx", "xls"], key="nc_upload")
            if uploaded:
                if not validate_file_size(uploaded, max_size_mb=50):
                    st.error(f"File exceeds 50 MB ({format_bytes(uploaded.size)}).")
                else:
                    try:
                        df = ingestion.load_file(uploaded)
                        st.session_state.data = df
                        st.session_state.current_step = max(st.session_state.current_step, 1)
                        st.success(f"Loaded {len(df):,} rows from `{uploaded.name}`.")
                    except Exception as exc:
                        st.error(f"Failed to read file: {exc}")

        elif src_choice == "Sample dataset":
            if st.button("Load sample dataset", type="primary", key="nc_sample"):
                with st.spinner("Loading sample data…"):
                    try:
                        df = ingestion.load_sample_data()
                        st.session_state.data = df
                        st.session_state.current_step = max(st.session_state.current_step, 1)
                        st.success(f"Loaded {len(df):,} sample complaints.")
                    except Exception as exc:
                        st.error(f"Failed: {exc}")

        elif src_choice == "API endpoint":
            api_url = st.text_input("API URL", placeholder="https://api.example.com/complaints")
            c1, c2 = st.columns(2)
            api_key = c1.text_input("API key (optional)", type="password")
            headers_json = c2.text_input("Extra headers (JSON)")
            if st.button("Fetch data", type="primary", key="nc_fetch"):
                if not api_url:
                    st.warning("Provide an API URL.")
                else:
                    with st.spinner("Fetching…"):
                        try:
                            df = ingestion.load_from_api(api_url, api_key or None, headers_json or None)
                            st.session_state.data = df
                            st.session_state.current_step = max(st.session_state.current_step, 1)
                            st.success(f"Fetched {len(df):,} rows.")
                        except Exception as exc:
                            st.error(f"API error: {exc}")

        else:
            st.caption("Continue to enter a single complaint manually.")

    if st.button("Continue", type="primary", key="nc_step0_next"):
        st.session_state.complaint_form_step = 1
        st.rerun()

elif step == 1:
    with st.form("manual_complaint_form", border=True):
        st.subheader("Complaint details")
        c1, c2 = st.columns(2)
        category = c1.selectbox(
            "Category",
            ["pothole", "streetlight", "garbage", "water_leakage", "drainage"],
        )
        ward = c2.text_input("Ward / location", placeholder="Jayanagar")
        description = st.text_area("Description", placeholder="Describe the civic issue…")
        c3, c4 = st.columns(2)
        lat = c3.number_input("Latitude", value=12.97, format="%.6f")
        lon = c4.number_input("Longitude", value=77.59, format="%.6f")
        attachment = st.file_uploader("Supporting documents (optional)", key="nc_attachment")
        submitted = st.form_submit_button("Continue to review", type="primary")

    if submitted:
        st.session_state.draft_complaint = {
            "category": category,
            "ward_name": ward,
            "description": description,
            "latitude": lat,
            "longitude": lon,
            "attachment_name": attachment.name if attachment else None,
        }
        st.session_state.complaint_form_step = 2
        st.rerun()

    if st.button("Back", key="nc_step1_back"):
        st.session_state.complaint_form_step = 0
        st.rerun()

else:
    with st.container(border=True):
        st.subheader("Review & submit")
        if st.session_state.data is not None:
            st.success(f"Dataset loaded — {len(st.session_state.data):,} complaints ready for analysis.")
            st.dataframe(st.session_state.data.head(10), use_container_width=True, hide_index=True)
        elif st.session_state.get("draft_complaint"):
            draft = st.session_state.draft_complaint
            st.json(draft)
            st.caption("Manual entries are stored as drafts until merged with a dataset import.")
        else:
            st.info("No complaint data to review yet.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back", key="nc_step2_back"):
            st.session_state.complaint_form_step = 1
            st.rerun()
    with c2:
        if st.button("Finish", type="primary", key="nc_finish"):
            st.session_state.complaint_form_step = 0
            st.toast("Complaint workflow complete.")
            st.rerun()
