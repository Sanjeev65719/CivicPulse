"""Shared session state and cached resources for CivicPulse."""

from __future__ import annotations

import os
import sys

import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.database_manager import DatabaseManager
from modules.ai_services import AIServices


@st.cache_resource
def get_db_manager(db_path: str):
    return DatabaseManager(db_path)


@st.cache_resource
def get_ai_services():
    return AIServices()


def init_session_state() -> None:
    db_path = os.path.join(PROJECT_ROOT, "civicpulse.db")
    defaults = {
        "authenticated": False,
        "user_name": "Operations Admin",
        "user_email": "admin@civicpulse.gov",
        "notify_email": True,
        "notify_sms": False,
        "data": None,
        "cleaned_data": None,
        "db_manager": get_db_manager(db_path),
        "ai_services": get_ai_services(),
        "hotspot_detector": None,
        "sla_predictor": None,
        "hotspot_results": None,
        "prediction_results": None,
        "current_step": 0,
        "complaint_form_step": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
