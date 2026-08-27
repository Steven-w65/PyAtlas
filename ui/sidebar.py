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
        st.header("Analyze a project")
        project_path = st.text_input(
            "Project path",
            key="project_path",
            placeholder=r"C:\path\to\python-project",
            help="Enter a local directory containing Python source files.",
        )
        ignore_text = st.text_area(
            "Additional ignore patterns",
            key="ignore_patterns",
            placeholder="generated/**\nlegacy_*.py",
            help="One project-relative glob pattern per line.",
        )
        analyze = st.button(
            "Analyze project",
            type="primary",
            use_container_width=True,
            key="analyze_project",
        )
        st.divider()
        st.subheader("Explore")
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
        st.caption("Analysis stays on this computer and never modifies source files.")

    return SidebarRequest(
        analyze=analyze,
        project_path=project_path.strip(),
        ignore_patterns=parse_ignore_patterns(ignore_text),
        risk_filter=risk_filter,
        graph_size_by="degree" if graph_size_label == "Dependency degree" else "score",
    )

