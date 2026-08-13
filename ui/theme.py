"""Stitch-inspired theme tokens and global CSS for CivicPulse."""

DESIGN = {
    "bg": "#0f1419",
    "bg_elevated": "#151b26",
    "sidebar": "#111820",
    "card": "#ffffff",
    "card_muted": "#f8fafc",
    "border": "#e2e8f0",
    "border_dark": "#1e293b",
    "text": "#0f172a",
    "text_muted": "#64748b",
    "text_on_dark": "#e2e8f0",
    "text_muted_on_dark": "#94a3b8",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "success": "#16a34a",
    "warning": "#ea580c",
    "danger": "#dc2626",
    "info": "#0284c7",
}


def inject_global_css() -> None:
    """Inject Stitch enterprise theme styles."""
    import streamlit as st

    d = DESIGN
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
}}

.stApp {{
    background: {d["bg"]};
    color: {d["text_on_dark"]};
}}

[data-testid="stAppViewContainer"] > .main {{
    background: radial-gradient(ellipse 80% 50% at 100% -20%, rgba(37,99,235,.12), transparent 55%), {d["bg"]};
}}

.block-container {{
    padding-top: 1.25rem;
    max-width: 1440px;
}}

[data-testid="stSidebar"] {{
    background: {d["sidebar"]};
    border-right: 1px solid {d["border_dark"]};
}}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {{
    color: {d["text_muted_on_dark"]};
}}

[data-testid="stSidebarNav"] {{
    background: transparent;
}}

[data-testid="stSidebarNav"] a {{
    color: {d["text_muted_on_dark"]} !important;
    border-radius: 8px;
    font-weight: 500;
}}

[data-testid="stSidebarNav"] a[aria-current="page"] {{
    background: rgba(37, 99, 235, 0.18) !important;
    color: #fff !important;
}}

.stButton > button, .stDownloadButton > button {{
    border-radius: 8px;
    font-weight: 600;
    min-height: 2.5rem;
    transition: all 0.15s ease;
}}

.stButton > button[kind="primary"] {{
    background: {d["primary"]};
    border: none;
    color: #fff;
}}

.stButton > button[kind="primary"]:hover {{
    background: {d["primary_hover"]};
    border: none;
    color: #fff;
}}

.stCard, div[data-testid="stMetric"] {{
    background: {d["card"]};
    color: {d["text"]};
    border: 1px solid {d["border"]};
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
}}

div[data-testid="stMetric"] label {{
    color: {d["text_muted"]} !important;
}}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {d["text"]} !important;
}}

[data-testid="stDataFrame"], [data-testid="stDataEditor"] {{
    border: 1px solid {d["border"]};
    border-radius: 12px;
    overflow: hidden;
    background: {d["card"]};
}}

[data-testid="stExpander"] {{
    background: {d["card"]};
    border: 1px solid {d["border"]};
    border-radius: 12px;
    color: {d["text"]};
}}

[data-testid="stExpander"] summary {{
    color: {d["text"]} !important;
}}

.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{
    border-radius: 8px;
}}

.page-hero {{
    background: linear-gradient(115deg, #1e3a8a 0%, {d["primary"]} 55%, #3b82f6 100%);
    padding: 1.5rem 1.75rem;
    border-radius: 14px;
    margin-bottom: 1.25rem;
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 12px 32px rgba(0,0,0,.2);
}}

.page-hero h1 {{
    color: #fff;
    font-weight: 700;
    font-size: 1.75rem;
    margin: 0;
}}

.page-hero p {{
    color: rgba(255,255,255,.85);
    font-size: .95rem;
    margin: .35rem 0 0;
}}

.surface-card {{
    background: {d["card"]};
    border: 1px solid {d["border"]};
    border-radius: 14px;
    padding: 1.15rem 1.25rem;
    color: {d["text"]};
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    min-height: 110px;
}}

.surface-card h3 {{
    font-size: .72rem;
    color: {d["text_muted"]};
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 600;
    margin: 0 0 .45rem;
}}

.surface-card .value {{
    font-size: 1.65rem;
    font-weight: 700;
    color: {d["text"]};
    margin: 0;
    line-height: 1.2;
}}

.surface-card .detail {{
    color: {d["text_muted"]};
    font-size: .82rem;
    margin-top: .35rem;
}}

.section-label {{
    color: {d["text_muted_on_dark"]};
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    margin-bottom: .65rem;
}}

.empty-state {{
    background: {d["card"]};
    border: 1px dashed {d["border"]};
    border-radius: 14px;
    padding: 2.5rem 2rem;
    text-align: center;
    color: {d["text_muted"]};
}}

.empty-state h3 {{
    color: {d["text"]};
    margin: 0 0 .5rem;
}}

.login-shell {{
    min-height: 78vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        linear-gradient(rgba(15,20,25,.72), rgba(15,20,25,.88)),
        url('https://images.unsplash.com/photo-1477959859467-3ac2d3c1ef34?auto=format&fit=crop&w=1600&q=80') center/cover no-repeat;
    border-radius: 16px;
    margin: -1rem -1rem 0;
    padding: 2rem;
}}

.login-card {{
    background: rgba(255,255,255,.97);
    border-radius: 16px;
    padding: 2rem 2.25rem;
    width: min(420px, 100%);
    box-shadow: 0 24px 48px rgba(0,0,0,.35);
    color: {d["text"]};
}}

.login-card h1 {{
    font-size: 1.5rem;
    margin: 0 0 .25rem;
    color: {d["text"]};
}}

.login-card .subtitle {{
    color: {d["text_muted"]};
    font-size: .9rem;
    margin-bottom: 1.5rem;
}}

.status-pill {{
    display: inline-block;
    padding: .2rem .65rem;
    border-radius: 999px;
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .02em;
}}

.status-resolved {{ background: #dcfce7; color: #166534; }}
.status-open {{ background: #fee2e2; color: #991b1b; }}
.status-progress {{ background: #ffedd5; color: #9a3412; }}
.status-pending {{ background: #fef9c3; color: #854d0e; }}

.priority-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}}

.priority-high {{ background: {d["danger"]}; }}
.priority-medium {{ background: {d["warning"]}; }}
.priority-low {{ background: {d["success"]}; }}

.filter-bar {{
    background: {d["card"]};
    border: 1px solid {d["border"]};
    border-radius: 12px;
    padding: .85rem 1rem;
    margin-bottom: 1rem;
}}

.stepper {{
    display: flex;
    gap: .5rem;
    margin-bottom: 1.25rem;
}}

.stepper-step {{
    flex: 1;
    text-align: center;
    padding: .65rem .5rem;
    border-radius: 8px;
    font-size: .78rem;
    font-weight: 600;
    background: {d["card_muted"]};
    color: {d["text_muted"]};
    border: 1px solid {d["border"]};
}}

.stepper-step.active {{
    background: {d["primary"]};
    color: #fff;
    border-color: {d["primary"]};
}}

.stepper-step.done {{
    background: #dbeafe;
    color: {d["primary"]};
    border-color: #93c5fd;
}}

#MainMenu, footer, header[data-testid="stHeader"] {{
    visibility: hidden;
}}
</style>
""",
        unsafe_allow_html=True,
    )
