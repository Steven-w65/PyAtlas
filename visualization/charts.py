"""Metric charts that consume completed project analysis."""

from __future__ import annotations

import plotly.graph_objects as go

from models import ProjectAnalysis


_CONFUSION_COLORS = ["#2A9D8F", "#8AB17D", "#E9C46A", "#F4A261", "#E76F51"]


def complexity_distribution(analysis: ProjectAnalysis) -> go.Figure:
    """Return function counts in the required complexity categories."""

    if not analysis.functions:
        return _empty_figure("Complexity Distribution")
    labels = ["Low", "Moderate", "High", "Very High"]
    counts = {label: 0 for label in labels}
    for function in analysis.functions:
        if function.complexity <= 5:
            counts["Low"] += 1
        elif function.complexity <= 10:
            counts["Moderate"] += 1
        elif function.complexity <= 20:
            counts["High"] += 1
        else:
            counts["Very High"] += 1
    figure = go.Figure(
        go.Bar(
            x=labels,
            y=[counts[label] for label in labels],
            marker_color=_CONFUSION_COLORS[1:],
            hovertemplate="%{x}: %{y} functions<extra></extra>",
        )
    )
    return _style(figure, "Complexity Distribution", "Functions")


def confusion_distribution(analysis: ProjectAnalysis) -> go.Figure:
    """Return function and module counts in the required score buckets."""

    values = [function.confusion_score for function in analysis.functions]
    values.extend(module.confusion_score for module in analysis.modules)
    if not values:
        return _empty_figure("Confusion Distribution")
    labels = ["0–20", "21–40", "41–60", "61–80", "81–100"]
    counts = [0, 0, 0, 0, 0]
    for value in values:
        index = min(int(max(value, 0) // 20), 4)
        if value > 0 and value % 20 == 0:
            index -= 1
        counts[max(index, 0)] += 1
    figure = go.Figure(
        go.Bar(
            x=labels,
            y=counts,
            marker_color=_CONFUSION_COLORS,
            hovertemplate="%{x}: %{y} symbols<extra></extra>",
        )
    )
    return _style(figure, "Confusion Distribution", "Symbols")


def size_vs_complexity(analysis: ProjectAnalysis) -> go.Figure:
    """Return module LOC versus average complexity with score-sized bubbles."""

    if not analysis.modules:
        return _empty_figure("File Size vs Complexity")
    modules = sorted(analysis.modules, key=lambda module: module.name)
    figure = go.Figure(
        go.Scatter(
            x=[module.lines for module in modules],
            y=[module.average_function_complexity for module in modules],
            mode="markers",
            customdata=[module.name for module in modules],
            marker={
                "size": [max(10.0, module.confusion_score / 2 + 8) for module in modules],
                "color": [module.confusion_score for module in modules],
                "colorscale": "RdYlGn_r",
                "cmin": 0,
                "cmax": 100,
                "showscale": True,
                "colorbar": {"title": "Score"},
                "line": {"width": 1, "color": "rgba(40,40,40,0.5)"},
            },
            hovertemplate=(
                "Module: %{customdata}<br>Lines: %{x}<br>"
                "Average complexity: %{y:.2f}<extra></extra>"
            ),
        )
    )
    return _style(
        figure,
        "File Size vs Complexity",
        "Average Complexity",
        x_title="Lines of Code",
    )


def dependency_risk(analysis: ProjectAnalysis) -> go.Figure:
    """Return module fan-in versus fan-out risk."""

    if not analysis.modules:
        return _empty_figure("Dependency Risk")
    modules = sorted(analysis.modules, key=lambda module: module.name)
    figure = go.Figure(
        go.Scatter(
            x=[module.fan_in for module in modules],
            y=[module.fan_out for module in modules],
            mode="markers+text",
            text=[module.name for module in modules],
            textposition="top center",
            customdata=[module.confusion_score for module in modules],
            marker={
                "size": [max(12.0, module.confusion_score / 2 + 8) for module in modules],
                "color": [module.confusion_score for module in modules],
                "colorscale": "RdYlGn_r",
                "cmin": 0,
                "cmax": 100,
                "showscale": False,
            },
            hovertemplate=(
                "%{text}<br>Fan-in: %{x}<br>Fan-out: %{y}<br>"
                "Score: %{customdata:.2f}<extra></extra>"
            ),
        )
    )
    return _style(figure, "Dependency Risk", "Fan-Out", x_title="Fan-In")


def _empty_figure(title: str) -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(
        text="No data available",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
    )
    return _style(figure, title, "")


def _style(
    figure: go.Figure,
    title: str,
    y_title: str,
    *,
    x_title: str = "",
) -> go.Figure:
    figure.update_layout(
        title={"text": title, "x": 0.02, "xanchor": "left"},
        xaxis_title=x_title,
        yaxis_title=y_title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 35, "r": 20, "t": 55, "b": 35},
        height=340,
    )
    return figure

