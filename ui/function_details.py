"""Selected-function metrics, recommendations, and source preview."""

from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st

from models import FunctionMetrics, ProjectAnalysis
from ui.module_details import contribution_rows
from ui.project_overview import score_band


def find_function(
    analysis: ProjectAnalysis,
    file_path: str,
    qualified_name: str,
) -> FunctionMetrics | None:
    """Return a function by its stable file-and-qualified-name identifier."""

    return next(
        (
            function
            for function in analysis.functions
            if function.file_path == file_path
            and function.qualified_name == qualified_name
        ),
        None,
    )


def source_excerpt(file_path: str, start_line: int, end_line: int) -> str:
    """Return a numbered UTF-8 source range or a user-readable error."""

    try:
        lines = Path(file_path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return f"Source preview unavailable: {type(exc).__name__}: {exc}"
    start = max(start_line, 1)
    stop = min(max(end_line, start), len(lines))
    return "\n".join(
        f"{number}: {lines[number - 1]}"
        for number in range(start, stop + 1)
    )


def render_function_details(
    analysis: ProjectAnalysis,
    file_path: str,
    qualified_name: str,
) -> None:
    """Render the complete function detail contract."""

    function = find_function(analysis, file_path, qualified_name)
    if function is None:
        st.info("Select a function to inspect its metrics and source.")
        return

    band_label, band_tone = score_band(function.confusion_score)
    st.markdown(
        f"""
        <div class="project-ribbon">
            <div>
                <div class="project-ribbon__eyebrow">Selected function</div>
                <div class="project-ribbon__name">{escape(function.qualified_name)}</div>
                <div class="project-ribbon__path">{escape(function.file_path)} · lines {function.start_line}–{function.end_line}</div>
            </div>
            <div class="risk-chip tone-{band_tone}">{band_label} · {function.confusion_score:.1f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(key="function_kpis"):
        first = st.columns(6, gap="small")
        first[0].metric("Confusion Score", f"{function.confusion_score:.2f}")
        first[1].metric("Complexity", function.complexity)
        first[2].metric("Lines", function.lines)
        first[3].metric("Nesting", function.nesting_depth)
        first[4].metric("Parameters", function.parameters)
        first[5].metric("Branches", function.branches)
        second = st.columns(6, gap="small")
        second[0].metric("Local Variables", function.local_variables)
        second[1].metric("Calls", function.calls)
        second[2].metric("Loops", function.loops)
        second[3].metric("Try Blocks", function.try_blocks)
        second[4].metric("Returns", function.returns)
        second[5].metric("Nested Functions", function.nested_functions)

    st.markdown("##### Why this score?")
    st.dataframe(
        contribution_rows(function.score_contributions),
        hide_index=True,
        width="stretch",
        column_config={
            "Risk %": st.column_config.ProgressColumn(
                min_value=0,
                max_value=100,
                format="%.1f",
            ),
            "Why": st.column_config.TextColumn(width="large"),
        },
    )

    issues = [
        issue
        for issue in analysis.issues
        if issue.file_path == function.file_path
        and issue.symbol_name == function.qualified_name
    ]
    st.markdown("##### Recommendations")
    if not issues:
        st.write("No function-level recommendations were triggered.")
    for issue in issues:
        st.warning(f"{issue.message} ({issue.severity})")

    with st.expander("Source preview", expanded=False):
        st.code(
            source_excerpt(function.file_path, function.start_line, function.end_line),
            language="python",
        )
