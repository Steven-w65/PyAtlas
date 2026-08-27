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
    risk_filter: str,
) -> dict[str, Any] | None:
    """Render overview content and return a newly selected hotspot row."""

    columns = st.columns(6)
    for column, (label, value) in zip(columns, summary_values(analysis).items(), strict=True):
        column.metric(label, value)

    left, right = st.columns(2)
    left.plotly_chart(confusion_distribution(analysis), use_container_width=True)
    right.plotly_chart(complexity_distribution(analysis), use_container_width=True)
    left, right = st.columns(2)
    left.plotly_chart(size_vs_complexity(analysis), use_container_width=True)
    right.plotly_chart(dependency_risk(analysis), use_container_width=True)

    st.subheader("Hotspots")
    rows = filter_hotspot_rows(hotspot_rows(analysis), risk_filter)
    if not rows:
        st.info("No functions or modules match the selected risk filter.")
        return None
    event = st.dataframe(
        rows,
        column_order=HOTSPOT_COLUMNS,
        hide_index=True,
        use_container_width=True,
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

