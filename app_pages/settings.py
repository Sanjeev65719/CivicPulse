"""User profile, settings & data pipeline — Stitch screen 6."""

import os

import pandas as pd
import streamlit as st

from modules.data_cleaning import DataCleaning
from ui.components import page_hero
from ui.state import PROJECT_ROOT


page_hero(
    "Profile & settings",
    "Manage your account, notifications, AI services, and data pipeline tools.",
)

tab_profile, tab_pipeline, tab_about = st.tabs([
    ":material/person: Profile",
    ":material/database: Data pipeline",
    ":material/info: About",
])

with tab_profile:
    with st.container(border=True):
        st.subheader("Personal information")
        st.session_state.user_name = st.text_input("Full name", st.session_state.user_name)
        st.session_state.user_email = st.text_input("Email", st.session_state.user_email)

    with st.container(border=True):
        st.subheader("Notification preferences")
        st.session_state.notify_email = st.toggle("Email alerts for SLA breaches", st.session_state.notify_email)
        st.session_state.notify_sms = st.toggle("SMS alerts for critical hotspots", st.session_state.notify_sms)

    with st.container(border=True):
        st.subheader("Security")
        st.text_input("Current password", type="password", disabled=True, placeholder="••••••••")
        if st.button("Send password reset link", key="settings_reset_pw"):
            st.toast("Password reset link sent to your email.")

    with st.container(border=True):
        st.subheader("Team management")
        team = pd.DataFrame([
            {"Name": st.session_state.user_name, "Role": "Admin", "Status": "Active"},
            {"Name": "Field Officer", "Role": "Operator", "Status": "Active"},
            {"Name": "Analyst", "Role": "Viewer", "Status": "Invited"},
        ])
        st.dataframe(team, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("AI service status")
    ai = st.session_state.ai_services
    token_info = ai.validate_token()
    if token_info["valid"]:
        st.success(token_info["message"])
    else:
        st.warning(token_info["message"])
    st.caption("Set `HF_API_KEY` to enable NLP queries.")

with tab_pipeline:
    working_df = st.session_state.cleaned_data if st.session_state.cleaned_data is not None else st.session_state.data

    with st.expander("Data cleaning", expanded=working_df is not None):
        if working_df is None:
            st.info("Load data first via **New complaint**.")
        else:
            cleaner = DataCleaning()
            df = st.session_state.data.copy()
            quality = cleaner.assess_data_quality(df)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Rows", f"{quality['total_rows']:,}")
            c2.metric("Columns", quality["total_columns"])
            c3.metric("Duplicates", quality["duplicate_count"])
            c4.metric("Invalid coords", quality["invalid_coordinates_count"])

            a1, a2 = st.columns(2)
            with a1:
                if st.button("Standardise columns", key="pipe_std_cols"):
                    st.session_state.data = cleaner.standardize_column_names(df)
                    st.toast("Columns standardised.")
            with a2:
                if st.button("Remove duplicates", key="pipe_rm_dup"):
                    before = len(df)
                    st.session_state.data = cleaner.remove_duplicates(df)
                    st.toast(f"Removed {before - len(st.session_state.data)} duplicates.")

            if st.button("Validate coordinates", key="pipe_coords"):
                st.session_state.data = cleaner.validate_coordinates(st.session_state.data)
                st.toast("Coordinates validated.")
            if st.button("Parse dates", key="pipe_dates"):
                st.session_state.data = cleaner.parse_dates(st.session_state.data)
                st.toast("Dates parsed.")
            if st.button("Finalize cleaned data", type="primary", key="pipe_finalize"):
                st.session_state.cleaned_data = st.session_state.data.copy()
                st.session_state.current_step = max(st.session_state.current_step, 2)
                st.success("Cleaned data saved.")

    with st.expander("Storage & queries"):
        if working_df is None:
            st.info("Load and clean data first.")
        else:
            db = st.session_state.db_manager
            table_name = st.text_input("Table name", value="complaints", key="pipe_table")
            if st.button("Save to SQLite", type="primary", key="pipe_save_db"):
                with st.spinner("Saving…"):
                    db.save_dataframe(working_df, table_name)
                    st.session_state.current_step = max(st.session_state.current_step, 3)
                st.success(f"Saved {len(working_df):,} rows.")

            nl_question = st.text_input("Natural-language query", placeholder="Which ward has the most complaints?")
            if st.button("Ask", key="pipe_ask_nl") and nl_question:
                schema_info = db.get_database_info()
                sql = st.session_state.ai_services.natural_language_to_sql(nl_question, schema_info)
                st.code(sql, language="sql")
                result = db.execute_query(sql)
                if not result.empty:
                    st.dataframe(result, use_container_width=True, hide_index=True)

            raw_sql = st.text_area("Raw SQL", placeholder="SELECT * FROM complaints LIMIT 10")
            if st.button("Execute SQL", key="pipe_exec_sql") and raw_sql:
                result = db.execute_query(raw_sql)
                if not result.empty:
                    st.dataframe(result, use_container_width=True, hide_index=True)

    with st.expander("Profiling report"):
        if working_df is None:
            st.info("Load data first.")
        elif st.button("Generate profile report", type="primary", key="pipe_profile"):
            from modules.profiling import DataProfiler

            profiler = DataProfiler()
            output_path = os.path.join(PROJECT_ROOT, "report.html")
            with st.spinner("Generating report…"):
                try:
                    path = profiler.generate_profile_report(working_df, output_path)
                    st.success(f"Report saved to `{path}`")
                    with open(path, "rb") as f:
                        st.download_button("Download report", f.read(), "civicpulse_profile.html", "text/html")
                except Exception as exc:
                    st.error(str(exc))

    st.divider()
    st.warning("Clearing session data resets all loaded datasets, models, and results.")
    if st.button("Clear all session data", key="settings_clear"):
        for key in list(st.session_state.keys()):
            if key not in {"authenticated", "user_name", "user_email", "notify_email", "notify_sms"}:
                del st.session_state[key]
        from ui.state import init_session_state

        init_session_state()
        st.session_state.authenticated = True
        st.success("Session cleared.")
        st.rerun()

with tab_about:
    st.markdown("""
**CivicPulse** — Municipal grievance & civic infrastructure analytics

| Component | Technology |
|---|---|
| UI | Streamlit (Stitch design) |
| Data | pandas, numpy |
| Storage | SQLAlchemy + SQLite |
| ML | scikit-learn (DBSCAN, Random Forest) |
| Charts | Plotly |
| NLP | Hugging Face Inference API (optional) |
    """)

    if st.session_state.sla_predictor and st.session_state.sla_predictor.is_trained:
        st.info("SLA prediction model is trained.")
    if st.session_state.hotspot_detector:
        st.info("Hotspot detector is configured.")

    if st.button("Sign out", key="settings_signout"):
        st.session_state.authenticated = False
        st.rerun()
