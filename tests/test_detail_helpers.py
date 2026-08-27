from pathlib import Path

import pytest

from services.analysis_service import AnalysisService
from ui.function_details import find_function, source_excerpt
from ui.module_details import contribution_rows, find_module, module_relations


SAMPLES = Path(__file__).parent / "sample_projects"


def test_source_excerpt_returns_requested_numbered_lines(tmp_path: Path) -> None:
    path = tmp_path / "sample.py"
    path.write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")

    assert source_excerpt(str(path), 2, 3) == "2: two\n3: three"


def test_source_excerpt_clamps_range_to_available_lines(tmp_path: Path) -> None:
    path = tmp_path / "sample.py"
    path.write_text("one\ntwo\n", encoding="utf-8")

    assert source_excerpt(str(path), 0, 20) == "1: one\n2: two"


def test_source_excerpt_reports_missing_file_without_raising(tmp_path: Path) -> None:
    text = source_excerpt(str(tmp_path / "missing.py"), 1, 2)

    assert text.startswith("Source preview unavailable: FileNotFoundError")


def test_module_relations_are_sorted() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")

    dependencies, dependents = module_relations(analysis, "helpers")

    assert dependencies == []
    assert dependents == ["app"]


def test_module_and_function_lookup_use_stable_identifiers() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    function = next(item for item in analysis.functions if item.qualified_name == "run")

    assert find_module(analysis, "app").name == "app"
    assert find_module(analysis, "missing") is None
    assert find_function(analysis, function.file_path, "run") == function
    assert find_function(analysis, function.file_path, "missing") is None


def test_contribution_rows_preserve_explanation_and_points() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    module = find_module(analysis, "app")

    rows = contribution_rows(module.score_contributions)

    assert list(rows[0]) == ["Metric", "Raw Value", "Risk %", "Weight %", "Points", "Why"]
    assert sum(row["Points"] for row in rows) == pytest.approx(
        module.confusion_score,
        abs=0.01,
    )
