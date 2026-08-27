"""Project summary cards, charts, and hotspot navigation."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any

import streamlit as st

from models import ProjectAnalysis
from visualization.charts import (
    complexity_distribution,
    confusion_distribution,
    dependency_risk,
    size_vs_complexity,
)


HOTSPOT_COLUMNS = [
    "Name",
    "Type",
    "File",
    "Confusion Score",
    "Complexity",
    "Lines",
    "Nesting",
    "Issues",
]


def score_band(score: float) -> tuple[str, str]:
    """Return the user-facing risk label and visual tone for a score."""

    if score <= 20:
        return "Very Easy", "low"
    if score <= 40:
        return "Easy", "guarded"
    if score <= 60:
        return "Moderate", "moderate"
    if score <= 80:
        return "Difficult", "high"
    return "Very Difficult", "critical"


def summary_values(analysis: ProjectAnalysis) -> OrderedDict[str, str | int]:
    """Return the six required project-card values in display order."""

    return OrderedDict(
        [
            ("Overall Confusion", f"{analysis.project_confusion_score:.1f}/100"),
            ("Python Files", analysis.python_file_count),
            ("Functions", analysis.function_count),
            ("Classes", analysis.class_count),
            ("Circular Dependencies", len(analysis.circular_dependencies)),
            (
                "High-risk Functions",
                sum(function.confusion_score > 60 for function in analysis.functions),
            ),
        ]
    )


def hotspot_rows(analysis: ProjectAnalysis) -> list[dict[str, Any]]:
    """Return module/function hotspot rows in descending score order."""

    rows: list[dict[str, Any]] = []
    for module in analysis.modules:
        rows.append(
            {
                "Name": module.name,
                "Type": "Module",
                "File": module.file_path,
                "Confusion Score": round(module.confusion_score, 2),
                "Complexity": round(module.average_function_complexity, 2),
                "Lines": module.lines,
                "Nesting": None,
                "Issues": _issue_count(analysis, module.file_path, module.name),
            }
        )
    for function in analysis.functions:
        rows.append(
            {
                "Name": function.qualified_name,
                "Type": "Function",
                "File": function.file_path,
                "Confusion Score": round(function.confusion_score, 2),
                "Complexity": function.complexity,
                "Lines": function.lines,
                "Nesting": function.nesting_depth,
                "Issues": _issue_count(
                    analysis,
                    function.file_path,
                    function.qualified_name,
                ),
            }
        )
    return sorted(
        rows,
        key=lambda row: (-row["Confusion Score"], row["Type"], row["Name"]),
    )


def filter_hotspot_rows(
    rows: list[dict[str, Any]],
    risk_filter: str,
) -> list[dict[str, Any]]:
    """Filter hotspot rows using the dashboard's explicit score boundaries."""

    thresholds = {
        "All": 0,
        "Moderate+ (41+)": 41,
        "High (61+)": 61,
        "Very High (81+)": 81,
    }
    threshold = thresholds.get(risk_filter, 0)
    return [row for row in rows if row["Confusion Score"] >= threshold]


def render_overview(
    analysis: ProjectAnalysis,
) -> None:
    """Render compact project metrics and risk-signal charts."""

    st.markdown(
        """
        <div class="atlas-section">
            <div>
                <div class="atlas-section__eyebrow">Project pulse</div>
                <div class="atlas-section__title">Health at a glance</div>
            </div>
            <div class="atlas-section__copy">A compact read on scale, structure, and the concentration of maintainability risk.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    summary_items = list(summary_values(analysis).items())
    with st.container(key="project_kpis"):
        columns = st.columns(6, gap="small")
        for column, (label, value) in zip(columns, summary_items, strict=True):
            column.metric(label, value)

    st.markdown(
        """
        <div class="atlas-section">
            <div>
                <div class="atlas-section__eyebrow">Signals</div>
                <div class="atlas-section__title">Risk landscape</div>
            </div>
            <div class="atlas-section__copy">Compare score shape, structural complexity, file scale, and dependency pressure.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns(2, gap="medium")
    left.plotly_chart(
        confusion_distribution(analysis),
        width="stretch",
        config={"displayModeBar": False},
    )
    right.plotly_chart(
        complexity_distribution(analysis),
        width="stretch",
        config={"displayModeBar": False},
    )
    left, right = st.columns(2, gap="medium")
    left.plotly_chart(
        size_vs_complexity(analysis),
        width="stretch",
        config={"displaylogo": False},
    )
    right.plotly_chart(
        dependency_risk(analysis),
        width="stretch",
        config={"displaylogo": False},
    )


def render_hotspots(
    analysis: ProjectAnalysis,
    risk_filter: str,
) -> dict[str, Any] | None:
    """Render the compact hotspot selector and return its selected row."""

    st.markdown(
        """
        <div class="explore-panel-heading">
            <div class="explore-panel-heading__title">Hotspots</div>
            <div class="explore-panel-heading__copy">Select a module or function to inspect.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    rows = filter_hotspot_rows(hotspot_rows(analysis), risk_filter)
    if not rows:
        st.info("No functions or modules match the selected risk filter.")
        return None
    event = st.dataframe(
        rows,
        column_order=HOTSPOT_COLUMNS,
        hide_index=True,
        width="stretch",
        height=400,
        column_config={
            "Confusion Score": st.column_config.ProgressColumn(
                "Risk",
                help="Explainable Confusion Score from 0 to 100.",
                min_value=0,
                max_value=100,
                format="%.1f",
            ),
            "File": st.column_config.TextColumn(width="large"),
            "Issues": st.column_config.NumberColumn(format="%d"),
        },
        on_select="rerun",
        selection_mode="single-row",
        key="hotspot_table",
    )
    selected_rows = getattr(getattr(event, "selection", None), "rows", [])
    if not selected_rows and isinstance(event, dict):
        selected_rows = event.get("selection", {}).get("rows", [])
    return rows[selected_rows[0]] if selected_rows else None


def _issue_count(
    analysis: ProjectAnalysis,
    file_path: str,
    symbol_name: str,
) -> int:
    return sum(
        issue.file_path == file_path and issue.symbol_name == symbol_name
        for issue in analysis.issues
    )
