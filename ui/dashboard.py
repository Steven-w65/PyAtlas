"""Top-level Streamlit dashboard composition and state transitions."""

from __future__ import annotations

from html import escape

import streamlit as st

from services import AnalysisService, ExportService
from ui.function_details import render_function_details
from ui.module_details import render_module_details
from ui.project_overview import render_overview, score_band
from ui.sidebar import render_sidebar
from ui.theme import APP_CSS
from visualization.dependency_graph import dependency_figure


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
    st.markdown(APP_CSS, unsafe_allow_html=True)
    st.title("PyAtlas")
    st.markdown(
        '<p class="atlas-lead">Map the architecture behind your Python code. '
        "Surface complexity, dependency pressure, and maintainability risk in one "
        "explainable workspace.</p><div class=\"atlas-rule\"></div>",
        unsafe_allow_html=True,
    )
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
                st.session_state.pop("module_detail_picker", None)
                st.session_state.pop("function_detail_picker", None)

    analysis = st.session_state.analysis
    if analysis is None:
        st.markdown(
            """
            <div class="welcome-grid">
                <div class="welcome-card">
                    <div class="welcome-card__index">01 · MAP</div>
                    <div class="welcome-card__title">See the architecture</div>
                    <div class="welcome-card__copy">Trace internal modules, fan-in, fan-out, and circular dependencies.</div>
                </div>
                <div class="welcome-card">
                    <div class="welcome-card__index">02 · PRIORITIZE</div>
                    <div class="welcome-card__title">Find meaningful hotspots</div>
                    <div class="welcome-card__copy">Rank modules and functions by transparent, metric-backed risk signals.</div>
                </div>
                <div class="welcome-card">
                    <div class="welcome-card__index">03 · UNDERSTAND</div>
                    <div class="welcome-card__title">Explain every score</div>
                    <div class="welcome-card__copy">Inspect contributions, recommendations, and source without leaving the map.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info(
            "Choose a local Python project in the sidebar to build its maintainability map.",
            icon="🧭",
        )
        return

    band_label, band_tone = score_band(analysis.project_confusion_score)
    st.markdown(
        f"""
        <div class="project-ribbon">
            <div>
                <div class="project-ribbon__eyebrow">Active analysis workspace</div>
                <div class="project-ribbon__name">{escape(analysis.project_name)}</div>
                <div class="project-ribbon__path">{escape(analysis.project_path)}</div>
            </div>
            <div class="risk-chip tone-{band_tone}">{band_label} · {analysis.project_confusion_score:.1f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "Confusion Score is a heuristic estimate based on structural code metrics. "
        "A high score does not automatically mean the code is poorly written.",
        icon="💡",
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

    st.markdown(
        """
        <div class="atlas-section">
            <div>
                <div class="atlas-section__eyebrow">Architecture</div>
                <div class="atlas-section__title">Dependency map</div>
            </div>
            <div class="atlas-section__copy">Select a node to highlight its direct dependencies and dependents.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        graph_event = st.plotly_chart(
            dependency_figure(
                analysis,
                selected_module=st.session_state.selected_module,
                size_by=request.graph_size_by,
            ),
            width="stretch",
            on_select="rerun",
            selection_mode="points",
            key="dependency_graph",
            config={"displaylogo": False, "scrollZoom": True},
        )
    graph_points = getattr(getattr(graph_event, "selection", None), "points", [])
    if not graph_points and isinstance(graph_event, dict):
        graph_points = graph_event.get("selection", {}).get("points", [])
    if graph_points:
        selected_name = graph_points[0].get("customdata")
        if isinstance(selected_name, (list, tuple)):
            selected_name = selected_name[0] if selected_name else None
        if selected_name in {module.name for module in analysis.modules}:
            st.session_state.selected_module = selected_name
            st.session_state.selected_function = None

    st.markdown(
        """
        <div class="atlas-section">
            <div>
                <div class="atlas-section__eyebrow">Deep dive</div>
                <div class="atlas-section__title">Inspect details</div>
            </div>
            <div class="atlas-section__copy">Move from the project view into module relationships, function metrics, and source.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    module_tab, function_tab = st.tabs(["◫  Module", "ƒ  Function"])
    with module_tab:
        module_names = [module.name for module in analysis.modules]
        if module_names:
            current_module = st.session_state.selected_module
            module_index = (
                module_names.index(current_module)
                if current_module in module_names
                else 0
            )
            module_name = st.selectbox(
                "Inspect module",
                module_names,
                index=module_index,
                key="module_detail_picker",
            )
            st.session_state.selected_module = module_name
            render_module_details(analysis, module_name)
        else:
            st.info("No analyzed modules are available.")

    with function_tab:
        function_options = {
            f"{function.qualified_name} · {function.file_path}:{function.start_line}": (
                function.file_path,
                function.qualified_name,
            )
            for function in analysis.functions
        }
        if function_options:
            labels = list(function_options)
            current_function = st.session_state.selected_function
            current_label = next(
                (
                    label
                    for label, identifier in function_options.items()
                    if identifier == current_function
                ),
                labels[0],
            )
            function_label = st.selectbox(
                "Inspect function",
                labels,
                index=labels.index(current_label),
                key="function_detail_picker",
            )
            function_identifier = function_options[function_label]
            st.session_state.selected_function = function_identifier
            render_function_details(analysis, *function_identifier)
        else:
            st.info("No analyzed functions are available.")

    st.markdown(
        """
        <div class="atlas-section">
            <div>
                <div class="atlas-section__eyebrow">Take it with you</div>
                <div class="atlas-section__title">Export analysis</div>
            </div>
            <div class="atlas-section__copy">Save the complete data model or share a focused hotspot list.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    export = ExportService()
    json_column, csv_column, _ = st.columns([1, 1.25, 3])
    json_column.download_button(
        "Download JSON",
        export.to_json(analysis),
        file_name=f"{analysis.project_name}-pyatlas.json",
        mime="application/json",
        width="stretch",
        icon=":material/data_object:",
    )
    csv_column.download_button(
        "Hotspots CSV",
        export.hotspot_csv(analysis),
        file_name=f"{analysis.project_name}-hotspots.csv",
        mime="text/csv",
        width="stretch",
        icon=":material/table_view:",
    )
