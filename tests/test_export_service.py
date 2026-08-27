import csv
import io
import json
from pathlib import Path

from models import ProjectAnalysis
from services.analysis_service import AnalysisService
from services.export_service import ExportService


SAMPLES = Path(__file__).parent / "sample_projects"


def test_json_contains_only_serializable_analysis_data() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")

    encoded = ExportService().to_json(analysis)
    payload = json.loads(encoded)

    assert payload["project_name"] == "simple_project"
    assert payload["dependency_edges"] == [["app", "helpers"]]
    assert isinstance(payload["modules"][0]["score_contributions"], list)
    assert encoded == ExportService().to_json(analysis)


def test_hotspot_csv_contains_function_and_module_rows() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")

    rows = list(csv.DictReader(io.StringIO(ExportService().hotspot_csv(analysis))))

    assert {row["Type"] for row in rows} == {"Function", "Module"}
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
    assert [float(row["Confusion Score"]) for row in rows] == sorted(
        [float(row["Confusion Score"]) for row in rows],
        reverse=True,
    )


def test_hotspot_csv_counts_symbol_issues() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "deep_nesting_project")

    rows = list(csv.DictReader(io.StringIO(ExportService().hotspot_csv(analysis))))
    function_row = next(row for row in rows if row["Type"] == "Function")

    assert function_row["Name"] == "deeply_nested"
    assert int(function_row["Issues"]) >= 1


def test_empty_analysis_exports_header_only_csv() -> None:
    analysis = ProjectAnalysis(
        project_name="empty",
        project_path="empty",
        python_file_count=0,
        total_lines=0,
        function_count=0,
        class_count=0,
        project_confusion_score=0,
        modules=[],
        functions=[],
        classes=[],
        issues=[],
        dependency_edges=[],
        circular_dependencies=[],
        errors=[],
    )

    assert ExportService().hotspot_csv(analysis).splitlines() == [
        "Name,Type,File,Confusion Score,Complexity,Lines,Nesting,Issues"
    ]
