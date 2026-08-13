"""Reusable UI components matching the Stitch design."""

from __future__ import annotations

import streamlit as st
import pandas as pd


def page_hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="page-hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, detail: str = "") -> str:
    detail_html = f'<div class="detail">{detail}</div>' if detail else ""
    return (
        f'<div class="surface-card"><h3>{label}</h3>'
        f'<p class="value">{value}</p>{detail_html}</div>'
    )


def empty_state(title: str, message: str) -> None:
    st.markdown(
        f'<div class="empty-state"><h3>{title}</h3><p>{message}</p></div>',
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    normalized = str(status).strip().lower()
    if normalized in {"resolved", "closed"}:
        css = "status-resolved"
        label = "Resolved"
    elif normalized in {"open"}:
        css = "status-open"
        label = "Open"
    elif normalized in {"in progress", "in_progress"}:
        css = "status-progress"
        label = "In Progress"
    else:
        css = "status-pending"
        label = status or "Pending"
    return f'<span class="status-pill {css}">{label}</span>'


def priority_badge(level: str) -> str:
    normalized = str(level).strip().lower()
    if "high" in normalized:
        css, label = "priority-high", "High"
    elif "medium" in normalized or "med" in normalized:
        css, label = "priority-medium", "Medium"
    else:
        css, label = "priority-low", "Low"
    return f'<span class="priority-dot {css}"></span>{label}'


def working_dataframe() -> pd.DataFrame | None:
    if st.session_state.cleaned_data is not None:
        return st.session_state.cleaned_data
    return st.session_state.data


def require_data(message: str = "Load complaint data from **New complaint** or **Settings → Data pipeline** first.") -> pd.DataFrame | None:
    df = working_dataframe()
    if df is None:
        empty_state("No data loaded", message)
    return df


def render_stepper(steps: list[str], current: int) -> None:
    parts = []
    for i, step in enumerate(steps):
        if i < current:
            cls = "stepper-step done"
        elif i == current:
            cls = "stepper-step active"
        else:
            cls = "stepper-step"
        parts.append(f'<div class="{cls}">{i + 1}. {step}</div>')
    st.markdown(f'<div class="stepper">{"".join(parts)}</div>', unsafe_allow_html=True)


def compute_priority(row: pd.Series) -> str:
    if row.get("breach_flag") == "High Risk":
        return "High"
    if row.get("breach_flag") == "Medium Risk":
        return "Medium"
    status = str(row.get("status", "")).lower()
    if status == "open":
        return "High"
    if status in {"in progress", "pending"}:
        return "Medium"
    return "Low"


def enrich_complaints(df: pd.DataFrame) -> pd.DataFrame:
    """Add display columns used across explorer and dashboard tables."""
    enriched = df.copy()
    if "priority" not in enriched.columns:
        enriched["priority"] = enriched.apply(compute_priority, axis=1)
    if "status_display" not in enriched.columns and "status" in enriched.columns:
        enriched["status_display"] = enriched["status"].astype(str)
    return enriched
