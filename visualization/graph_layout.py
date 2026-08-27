"""Deterministic dependency graph layout."""

from __future__ import annotations

import networkx as nx


def graph_positions(graph: nx.DiGraph) -> dict[str, tuple[float, float]]:
    """Return stable spring-layout coordinates for every graph node."""

    if not graph.nodes:
        return {}
    positions = nx.spring_layout(graph, seed=42)
    return {
        name: (round(float(value[0]), 8), round(float(value[1]), 8))
        for name, value in sorted(positions.items())
    }

