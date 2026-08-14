"""
CivicPulse — Municipal Grievance & Civic Infrastructure Analytics Agent

Stitch-inspired multi-page Streamlit application with executive dashboard,
geospatial analysis, complaint explorer, trends, manual entry, and settings.
"""

import streamlit as st

from ui.state import init_session_state
from ui.theme import inject_global_css

st.set_page_config(
    page_title="CivicPulse — Executive Overview",
    page_icon=":material/account_balance:",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
inject_global_css()


def render_login() -> None:
    st.markdown(
        """
<div class="login-shell">
  <div class="login-card">
    <h1>CivicPulse</h1>
    <p class="subtitle">Secure access to municipal analytics & operations</p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    _, center, _ = st.columns((1, 1.2, 1))
    with center:
        with st.container(border=True):
            st.markdown("#### Sign in")
            email = st.text_input("Email", value=st.session_state.user_email, key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_pw")
            st.caption("Demo credentials: admin@civicpulse.gov / civicpulse")
            if st.button("Sign in", type="primary", use_container_width=True, key="login_submit"):
                if email and password == "civicpulse":
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("Invalid credentials. Use password `civicpulse` for demo access.")


if not st.session_state.authenticated:
    render_login()
    st.stop()

with st.sidebar:
    st.markdown("### :material/account_balance: CivicPulse")
    st.caption("Municipal analytics")
    if st.session_state.data is not None:
        df = st.session_state.data
        st.metric("Loaded rows", f"{len(df):,}")
        if "category" in df.columns:
            st.metric("Categories", df["category"].nunique())
    st.divider()
    st.caption(f"Signed in as **{st.session_state.user_name}**")

page = st.navigation(
    {
        "Operations": [
            st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:"),
            st.Page("app_pages/geospatial.py", title="Geospatial", icon=":material/map:"),
            st.Page("app_pages/explorer.py", title="Explorer", icon=":material/table_chart:"),
            st.Page("app_pages/trends.py", title="Trends", icon=":material/query_stats:"),
        ],
        "Management": [
            st.Page("app_pages/new_complaint.py", title="New complaint", icon=":material/add_circle:"),
            st.Page("app_pages/settings.py", title="Settings", icon=":material/settings:"),
        ],
    },
    position="sidebar",
)

page.run()

if __name__=="__main__":
    app.run()  # type: ignore
app=app  # type: ignore