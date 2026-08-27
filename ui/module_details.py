"""Selected-module metrics, relationships, and score explanations."""

from __future__ import annotations

from typing import Any

import streamlit as st

from models import ModuleMetrics, ProjectAnalysis, ScoreContribution


def find_module(
    analysis: ProjectAnalysis,
    module_name: str | None,
) -> ModuleMetrics | None:
    """Return a module by its stable project-relative name."""

    return next(
        (module for module in analysis.modules if module.name == module_name),
        None,
    )


def module_relations(
    analysis: ProjectAnalysis,
    module_name: str,
) -> tuple[list[str], list[str]]:
    """Return sorted direct dependencies and dependents for one module."""

    dependencies = sorted(
        target
        for source, target in analysis.dependency_edges
        if source == module_name
    )
    dependents = sorted(
        source
        for source, target in analysis.dependency_edges
        if target == module_name
    )
    return dependencies, dependents


def contribution_rows(
    contributions: list[ScoreContribution],
) -> list[dict[str, Any]]:
    """Convert score contributions to display-ready explanatory rows."""

    return [
        {
            "Metric": item.metric,
            "Raw Value": round(item.raw_value, 2),
            "Risk %": round(item.normalized_value, 2),
            "Weight %": round(item.weight * 100, 1),
            "Points": round(item.points, 4),
            "Why": item.reason,
        }
        for item in sorted(contributions, key=lambda value: -value.points)
    ]


def render_module_details(analysis: ProjectAnalysis, module_name: str) -> None:
    """Render the complete module detail contract."""

    module = find_module(analysis, module_name)
    if module is None:
        st.info("Select a module to inspect its metrics and dependencies.")
        return

    st.markdown(f"#### `{module.name}`")
    st.caption(module.file_path)
    first = st.columns(4)
    first[0].metric("Confusion Score", f"{module.confusion_score:.2f}")
    first[1].metric("Lines", module.lines)
    first[2].metric("Functions", module.function_count)
    first[3].metric("Classes", module.class_count)
    second = st.columns(4)
    second[0].metric("Fan-In", module.fan_in)
    second[1].metric("Fan-Out", module.fan_out)
    second[2].metric(
        "Maintainability Index",
        "Unavailable"
        if module.maintainability_index is None
        else f"{module.maintainability_index:.2f}",
    )
    second[3].metric("Max Complexity", module.max_function_complexity)

    dependencies, dependents = module_relations(analysis, module.name)
    left, right = st.columns(2)
    left.markdown("**Dependencies**")
    left.write(", ".join(f"`{name}`" for name in dependencies) or "None")
    right.markdown("**Dependents**")
    right.write(", ".join(f"`{name}`" for name in dependents) or "None")
    if module.external_imports:
        st.caption("External imports: " + ", ".join(module.external_imports))

    st.markdown("**Why this score?**")
    st.dataframe(
        contribution_rows(module.score_contributions),
        hide_index=True,
        use_container_width=True,
    )
    _render_issues(analysis, module.file_path, module.name)


def _render_issues(
    analysis: ProjectAnalysis,
    file_path: str,
    symbol_name: str,
) -> None:
    issues = [
        issue
        for issue in analysis.issues
        if issue.file_path == file_path and issue.symbol_name == symbol_name
    ]
    st.markdown("**Recommendations**")
    if not issues:
        st.write("No module-level recommendations were triggered.")
        return
    for issue in issues:
        st.warning(f"{issue.message} ({issue.severity})")

