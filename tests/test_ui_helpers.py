from pathlib import Path

import ui.project_overview as project_overview
from services.analysis_service import AnalysisService
from ui.project_overview import (
    filter_hotspot_rows,
    hotspot_rows,
    summary_values,
)
from ui.sidebar import parse_ignore_patterns


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
