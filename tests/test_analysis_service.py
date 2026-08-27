from dataclasses import asdict
from pathlib import Path

import pytest

from analyzer.duplication_analyzer import DuplicateMatch, DuplicationAnalyzer
from services.analysis_service import AnalysisService


SAMPLES = Path(__file__).parent / "sample_projects"


def test_analyze_simple_project_returns_complete_metrics() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")

    assert analysis.project_name == "simple_project"
    assert analysis.python_file_count == 2
    assert analysis.total_lines > 0
    assert analysis.function_count == 2
    assert analysis.class_count == 1
    assert {module.name for module in analysis.modules} == {"app", "helpers"}
    assert analysis.dependency_edges == [("app", "helpers")]
    assert analysis.circular_dependencies == []
    assert 0 <= analysis.project_confusion_score <= 100
    assert all(function.complexity >= 1 for function in analysis.functions)
    assert all(function.score_contributions for function in analysis.functions)
    assert all(module.score_contributions for module in analysis.modules)


def test_analyze_project_detects_cycle_and_generates_cycle_issue() -> None:
    analysis = AnalysisService().analyze_project(
        SAMPLES / "circular_import_project",
    )

    assert analysis.circular_dependencies == [["a", "b"]]
    assert sorted(analysis.dependency_edges) == [("a", "b"), ("b", "a")]
    assert all(module.circular_dependency_count == 1 for module in analysis.modules)
    assert "circular_dependency" in {issue.issue_type for issue in analysis.issues}


def test_syntax_error_is_collected_while_valid_file_is_analyzed() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "syntax_error_project")

    assert analysis.python_file_count == 2
    assert analysis.function_count == 1
    assert {function.qualified_name for function in analysis.functions} == {"valid"}
    assert any("broken.py:1: SyntaxError" in error for error in analysis.errors)


def test_default_ignored_folder_is_excluded_from_full_analysis() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "ignored_folders_project")

    assert analysis.python_file_count == 1
    assert analysis.function_count == 1
    assert analysis.modules[0].name == "visible"


def test_deep_nesting_generates_recommendation() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "deep_nesting_project")

    function = analysis.functions[0]
    assert function.nesting_depth == 5
    assert "deep_nesting" in {issue.issue_type for issue in analysis.issues}


def test_analysis_is_deterministic() -> None:
    service = AnalysisService()

    first = service.analyze_project(SAMPLES / "simple_project")
    second = service.analyze_project(SAMPLES / "simple_project")

    assert asdict(first) == asdict(second)


def test_invalid_project_path_uses_user_facing_error(tmp_path: Path) -> None:
    with pytest.raises(
        ValueError,
        match="Project path does not exist or is not a directory",
    ):
        AnalysisService().analyze_project(tmp_path / "missing")


def test_duplicate_module_names_use_a_user_facing_error(tmp_path: Path) -> None:
    """Catch one source file silently replacing another analysis record."""

    (tmp_path / "pkg.py").write_text("VALUE = 'module'\n", encoding="utf-8")
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "__init__.py").write_text("VALUE = 'package'\n", encoding="utf-8")

    with pytest.raises(ValueError, match=r"Module name collision.*pkg"):
        AnalysisService().analyze_project(tmp_path)


def test_duplication_interface_is_reserved_but_deferred() -> None:
    match = DuplicateMatch("a.py", "a", "b.py", "b", 0.9)
    assert match.similarity == 0.9

    with pytest.raises(NotImplementedError, match="deferred"):
        DuplicationAnalyzer().compare_functions([], {})
