from pathlib import Path

import plotly.graph_objects as go

from models import ProjectAnalysis
from services.analysis_service import AnalysisService
from visualization.charts import (
    complexity_distribution,
    confusion_distribution,
    dependency_risk,
    size_vs_complexity,
)
from visualization.dependency_graph import dependency_figure
from visualization.graph_layout import graph_positions


SAMPLES = Path(__file__).parent / "sample_projects"


def empty_analysis() -> ProjectAnalysis:
    return ProjectAnalysis(
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


def test_complexity_distribution_uses_required_buckets() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")

    figure = complexity_distribution(analysis)

    assert isinstance(figure, go.Figure)
    assert list(figure.data[0].x) == ["Low", "Moderate", "High", "Very High"]
    assert sum(figure.data[0].y) == analysis.function_count


def test_confusion_distribution_uses_required_buckets() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")

    figure = confusion_distribution(analysis)

    assert list(figure.data[0].x) == ["0–20", "21–40", "41–60", "61–80", "81–100"]
    assert sum(figure.data[0].y) == len(analysis.functions) + len(analysis.modules)


def test_scatter_and_dependency_risk_render_module_points() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")

    size_figure = size_vs_complexity(analysis)
    risk_figure = dependency_risk(analysis)

    assert len(size_figure.data[0].x) == len(analysis.modules)
    assert len(risk_figure.data[0].x) == len(analysis.modules)


def test_graph_positions_are_deterministic() -> None:
    import networkx as nx

    graph = nx.DiGraph([("a", "b"), ("b", "c")])

    assert graph_positions(graph) == graph_positions(graph)


def test_dependency_graph_preserves_nodes_and_selection_metadata() -> None:
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")

    figure = dependency_figure(analysis, selected_module="app")
    node_trace = figure.data[-1]

    assert set(node_trace.customdata) == {"app", "helpers"}
    assert "Module" in node_trace.hovertemplate
    colors = dict(zip(node_trace.customdata, node_trace.marker.color, strict=True))
    assert colors["app"] != colors["helpers"]


def test_dashboard_visualizations_fit_the_compact_layout() -> None:
    """Catch charts regrowing enough to push Explore below the next viewport."""

    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    signal_figures = [
        complexity_distribution(analysis),
        confusion_distribution(analysis),
        size_vs_complexity(analysis),
        dependency_risk(analysis),
    ]

    assert {figure.layout.height for figure in signal_figures} == {285}
    assert dependency_figure(analysis).layout.height == 400


def test_all_visualizations_handle_empty_data() -> None:
    analysis = empty_analysis()
    figures = [
        complexity_distribution(analysis),
        confusion_distribution(analysis),
        size_vs_complexity(analysis),
        dependency_risk(analysis),
        dependency_figure(analysis),
    ]

    assert all(figure.layout.annotations[0].text == "No data available" for figure in figures)
