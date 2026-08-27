from pathlib import Path

import ui.project_overview as project_overview
from services.analysis_service import AnalysisService
from ui.dashboard import synchronize_hotspot_selection
from ui.project_overview import (
    filter_hotspot_rows,
    hotspot_rows,
    summary_values,
)
from ui.sidebar import parse_ignore_patterns
from visualization.charts import complexity_distribution
from visualization.dependency_graph import dependency_figure


SAMPLES = Path(__file__).parent / "sample_projects"


def test_hotspot_rows_have_required_columns_and_descending_scores() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")

    rows = hotspot_rows(analysis)

    assert list(rows[0]) == [
        "Name",
        "Type",
        "File",
        "Confusion Score",
        "Complexity",
        "Lines",
        "Nesting",
        "Issues",
    ]
    scores = [row["Confusion Score"] for row in rows]
    assert scores == sorted(scores, reverse=True)
    assert {row["Type"] for row in rows} == {"Function", "Module"}


def test_hotspot_rows_include_real_issue_counts() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "deep_nesting_project")

    row = next(item for item in hotspot_rows(analysis) if item["Type"] == "Function")

    assert row["Name"] == "deeply_nested"
    assert row["Issues"] >= 1


def test_summary_values_include_all_required_cards() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")

    values = summary_values(analysis)

    assert list(values) == [
        "Overall Confusion",
        "Python Files",
        "Functions",
        "Classes",
        "Circular Dependencies",
        "High-risk Functions",
    ]
    assert values["Python Files"] == 2
    assert values["Functions"] == 2
    assert values["Classes"] == 1


def test_risk_filter_uses_score_boundaries() -> None:
    rows = [
        {"Name": "easy", "Confusion Score": 20.0},
        {"Name": "moderate", "Confusion Score": 41.0},
        {"Name": "difficult", "Confusion Score": 61.0},
        {"Name": "very-difficult", "Confusion Score": 81.0},
    ]

    assert [row["Name"] for row in filter_hotspot_rows(rows, "Moderate+ (41+)")] == [
        "moderate",
        "difficult",
        "very-difficult",
    ]
    assert [row["Name"] for row in filter_hotspot_rows(rows, "Very High (81+)")] == [
        "very-difficult"
    ]


def test_parse_ignore_patterns_strips_blanks_and_preserves_order() -> None:
    assert parse_ignore_patterns(" generated/** \n\nlegacy_*.py\n") == [
        "generated/**",
        "legacy_*.py",
    ]


def test_score_band_uses_the_documented_risk_boundaries() -> None:
    """Catch dashboard labels drifting away from the score ranges users see."""

    assert hasattr(project_overview, "score_band")
    assert [
        project_overview.score_band(score)
        for score in (0, 20, 21, 40, 41, 60, 61, 80, 81, 100)
    ] == [
        ("Very Easy", "low"),
        ("Very Easy", "low"),
        ("Easy", "guarded"),
        ("Easy", "guarded"),
        ("Moderate", "moderate"),
        ("Moderate", "moderate"),
        ("Difficult", "high"),
        ("Difficult", "high"),
        ("Very Difficult", "critical"),
        ("Very Difficult", "critical"),
    ]


def test_visualizations_delegate_text_surfaces_to_streamlit_theme() -> None:
    """Catch figures pinning dark-mode text and hover colors in light mode."""

    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")

    for figure in (complexity_distribution(analysis), dependency_figure(analysis)):
        assert figure.layout.font.color is None
        assert figure.layout.title.font.color is None
        assert figure.layout.hoverlabel.bgcolor is None
        assert figure.layout.hoverlabel.bordercolor is None
        assert figure.layout.hoverlabel.font.color is None


def test_hotspot_function_selection_updates_graph_on_first_rerun_and_clears_on_deselect() -> None:
    """Catch graph highlighting lagging one rerun behind Hotspots selection."""

    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    function = next(
        item
        for item in hotspot_rows(analysis)
        if item["Type"] == "Function" and item["Name"] == "run"
    )
    state = {
        "hotspot_selection": None,
        "graph_selected_module": None,
        "selected_module": None,
        "selected_function": None,
    }

    synchronize_hotspot_selection(state, analysis, function)

    assert state["graph_selected_module"] == "app"
    assert state["selected_module"] == "app"
    assert state["selected_function"] == (function["File"], function["Name"])

    state["graph_selected_module"] = "helpers"
    synchronize_hotspot_selection(state, analysis, function)
    assert state["graph_selected_module"] == "helpers"

    synchronize_hotspot_selection(state, analysis, None)

    assert state["graph_selected_module"] is None
    assert state["selected_module"] == "app"
    assert state["selected_function"] == (function["File"], function["Name"])


def test_hotspot_module_selection_targets_the_selected_module() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    module = next(
        item
        for item in hotspot_rows(analysis)
        if item["Type"] == "Module" and item["Name"] == "helpers"
    )
    state = {
        "hotspot_selection": None,
        "graph_selected_module": None,
        "selected_module": None,
        "selected_function": ("old.py", "old"),
    }

    synchronize_hotspot_selection(state, analysis, module)

    assert state["graph_selected_module"] == "helpers"
    assert state["selected_module"] == "helpers"
    assert state["selected_function"] is None
