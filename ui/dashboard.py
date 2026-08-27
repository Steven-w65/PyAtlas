"""Top-level Streamlit dashboard composition and state transitions."""

from __future__ import annotations

import streamlit as st

from services import AnalysisService, ExportService
from ui.project_overview import render_overview
from ui.sidebar import render_sidebar


SESSION_DEFAULTS = {
    "project_path": "",
    "analysis": None,
    "selected_module": None,
    "selected_function": None,
    "risk_filter": "All",
    "graph_size_label": "Confusion score",
    "ignore_patterns": "",
}


def initialize_session_state() -> None:
    """Populate required session keys without replacing existing analysis."""

    for key, value in SESSION_DEFAULTS.items():
        st.session_state.setdefault(key, value)


def render_dashboard() -> None:
    """Compose controls, analysis results, exports, and navigation state."""

    initialize_session_state()
    st.title("PyAtlas")
    st.caption("Interactive, explainable maintainability mapping for Python projects")
    request = render_sidebar()

    if request.analyze:
        if not request.project_path:
            st.error("Enter a local Python project path before analyzing.")
        else:
            try:
                with st.spinner("Mapping project structure and maintainability risk…"):
                    result = AnalysisService().analyze_project(
                        request.project_path,
                        extra_ignore_patterns=request.ignore_patterns,
                    )
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.session_state.analysis = result
                st.session_state.selected_module = None
                st.session_state.selected_function = None

    analysis = st.session_state.analysis
    if analysis is None:
        st.info("Choose a local Python project in the sidebar to build its maintainability map.")
        return

    st.markdown(f"### {analysis.project_name}")
    st.caption(analysis.project_path)
    st.info(
        "Confusion Score is a heuristic estimate based on structural code metrics. "
        "A high score does not automatically mean the code is poorly written.",
        icon="ℹ️",
    )
    if analysis.errors:
        with st.expander(f"Partial analysis warnings ({len(analysis.errors)})"):
            for error in analysis.errors:
                st.code(error, language=None)

    selected = render_overview(analysis, request.risk_filter)
    if selected:
        if selected["Type"] == "Module":
            st.session_state.selected_module = selected["Name"]
            st.session_state.selected_function = None
        else:
            st.session_state.selected_function = (selected["File"], selected["Name"])
            st.session_state.selected_module = None

    export = ExportService()
    json_column, csv_column, _ = st.columns([1, 1, 3])
    json_column.download_button(
        "Download JSON",
        export.to_json(analysis),
        file_name=f"{analysis.project_name}-pyatlas.json",
        mime="application/json",
        use_container_width=True,
    )
    csv_column.download_button(
        "Download hotspot CSV",
        export.hotspot_csv(analysis),
        file_name=f"{analysis.project_name}-hotspots.csv",
        mime="text/csv",
        use_container_width=True,
    )

