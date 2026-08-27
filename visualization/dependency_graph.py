"""Interactive Plotly representation of internal module dependencies."""

from __future__ import annotations

import networkx as nx
import plotly.graph_objects as go

from models import ModuleMetrics, ProjectAnalysis
from visualization.graph_layout import graph_positions


def dependency_figure(
    analysis: ProjectAnalysis,
    selected_module: str | None = None,
    size_by: str = "score",
) -> go.Figure:
    """Build a selectable dependency graph with relationship highlighting."""

    if not analysis.modules:
        return _empty_graph()
    graph = nx.DiGraph()
    graph.add_nodes_from(module.name for module in analysis.modules)
    graph.add_edges_from(analysis.dependency_edges)
    positions = graph_positions(graph)
    modules = {module.name: module for module in analysis.modules}

    dependencies = (
        set(graph.successors(selected_module))
        if selected_module in graph
        else set()
    )
    dependents = (
        set(graph.predecessors(selected_module))
        if selected_module in graph
        else set()
    )
    figure = go.Figure()
    figure.add_trace(_edge_trace(graph, positions, selected_module, "all"))
    if selected_module in graph:
        figure.add_trace(_edge_trace(graph, positions, selected_module, "highlighted"))

    names = sorted(graph.nodes)
    figure.add_trace(
        go.Scatter(
            x=[positions[name][0] for name in names],
            y=[positions[name][1] for name in names],
            mode="markers+text",
            text=[_short_name(name) for name in names],
            textposition="top center",
            customdata=names,
            hovertext=[_module_hover(modules[name]) for name in names],
            hovertemplate="Module: %{customdata}<br>%{hovertext}<extra></extra>",
            marker={
                "size": [_node_size(modules[name], graph, size_by) for name in names],
                "color": [
                    _node_color(name, modules[name], selected_module, dependencies, dependents)
                    for name in names
                ],
                "line": {"width": 1.5, "color": "rgba(35,35,35,0.65)"},
            },
            name="Modules",
        )
    )
    figure.update_layout(
        title={"text": "Internal Dependency Map", "x": 0.02, "xanchor": "left"},
        showlegend=False,
        hovermode="closest",
        clickmode="event+select",
        dragmode="pan",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 15, "r": 15, "t": 55, "b": 15},
        height=520,
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
    return figure


def _edge_trace(
    graph: nx.DiGraph,
    positions: dict[str, tuple[float, float]],
    selected_module: str | None,
    mode: str,
) -> go.Scatter:
    x_values: list[float | None] = []
    y_values: list[float | None] = []
    for source, target in sorted(graph.edges):
        related = selected_module is not None and selected_module in {source, target}
        if (mode == "highlighted") != related:
            continue
        x_values.extend([positions[source][0], positions[target][0], None])
        y_values.extend([positions[source][1], positions[target][1], None])
    return go.Scatter(
        x=x_values,
        y=y_values,
        mode="lines",
        line={
            "width": 3 if mode == "highlighted" else 1,
            "color": "#457B9D" if mode == "highlighted" else "rgba(120,120,120,0.35)",
        },
        hoverinfo="skip",
        name="Dependencies",
    )


def _node_size(module: ModuleMetrics, graph: nx.DiGraph, size_by: str) -> float:
    if size_by.lower() == "degree":
        return 18 + (graph.in_degree(module.name) + graph.out_degree(module.name)) * 5
    return 18 + module.confusion_score * 0.32


def _node_color(
    name: str,
    module: ModuleMetrics,
    selected_module: str | None,
    dependencies: set[str],
    dependents: set[str],
) -> str:
    if name == selected_module:
        return "#277DA1"
    if name in dependencies:
        return "#43AA8B"
    if name in dependents:
        return "#F8961E"
    if module.confusion_score <= 20:
        return "#2A9D8F"
    if module.confusion_score <= 40:
        return "#8AB17D"
    if module.confusion_score <= 60:
        return "#E9C46A"
    if module.confusion_score <= 80:
        return "#F4A261"
    return "#E76F51"


def _module_hover(module: ModuleMetrics) -> str:
    return (
        f"Confusion score: {module.confusion_score:.2f}<br>"
        f"Lines: {module.lines}<br>Functions: {module.function_count}<br>"
        f"Classes: {module.class_count}<br>Fan-in: {module.fan_in}<br>"
        f"Fan-out: {module.fan_out}"
    )


def _short_name(name: str) -> str:
    return name if len(name) <= 24 else f"…{name[-23:]}"


def _empty_graph() -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(
        text="No data available",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
    )
    figure.update_layout(
        title="Internal Dependency Map",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=520,
    )
    return figure
