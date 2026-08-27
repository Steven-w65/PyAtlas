"""Sidebar controls for starting and filtering project analysis."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class SidebarRequest:
    analyze: bool
    project_path: str
    ignore_patterns: list[str]
    risk_filter: str
    graph_size_by: str


def parse_ignore_patterns(value: str) -> list[str]:
    """Parse newline-separated ignore patterns in user-entered order."""

    return [line.strip() for line in value.splitlines() if line.strip()]


def render_sidebar() -> SidebarRequest:
    """Render project controls and return the current request state."""

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand__mark">A</div>
                <div>
                    <div class="sidebar-brand__name">PyAtlas</div>
                    <div class="sidebar-brand__meta">Code observatory</div>
                </div>
            </div>
            <div class="sidebar-eyebrow">Scan target</div>
            """,
            unsafe_allow_html=True,
        )
        project_path = st.text_input(
            "Local project path",
            key="project_path",
            placeholder=r"C:\path\to\python-project",
            help="Enter a local directory containing Python source files.",
        )
        ignore_text = st.text_area(
            "Ignore patterns",
            key="ignore_patterns",
            placeholder="generated/**\nlegacy_*.py",
            help="One project-relative glob pattern per line.",
        )
        analyze = st.button(
            "Analyze project",
            type="primary",
            width="stretch",
            key="analyze_project",
            icon=":material/travel_explore:",
        )
        st.divider()
        st.markdown(
            '<div class="sidebar-eyebrow">View controls</div>',
            unsafe_allow_html=True,
        )
        risk_filter = st.selectbox(
            "Risk filter",
            ["All", "Moderate+ (41+)", "High (61+)", "Very High (81+)"],
            key="risk_filter",
        )
        graph_size_label = st.selectbox(
            "Graph node size",
            ["Confusion score", "Dependency degree"],
            key="graph_size_label",
        )
        st.markdown(
            """
            <div class="privacy-note">
                <strong>Local by design.</strong><br>
                Source stays on this computer. PyAtlas reads files for analysis and never modifies them.
            </div>
            """,
            unsafe_allow_html=True,
        )

    return SidebarRequest(
        analyze=analyze,
        project_path=project_path.strip(),
        ignore_patterns=parse_ignore_patterns(ignore_text),
        risk_filter=risk_filter,
        graph_size_by="degree" if graph_size_label == "Dependency degree" else "score",
    )
