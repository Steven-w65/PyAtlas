"""Internal module resolution and dependency graph analysis."""

from __future__ import annotations

from pathlib import Path

import networkx as nx


class DependencyAnalyzer:
    """Build and inspect a directed graph of internal Python imports."""

    def build_graph(
        self,
        module_names: set[str],
        imports_by_module: dict[str, list[str]],
    ) -> nx.DiGraph:
        """Return a graph containing all modules and internal import edges."""

        graph = nx.DiGraph()
        graph.add_nodes_from(sorted(module_names))
        for source in sorted(module_names):
            for target in sorted(set(imports_by_module.get(source, []))):
                if target in module_names and target != source:
                    graph.add_edge(source, target)
        return graph

    def find_cycles(self, graph: nx.DiGraph) -> list[list[str]]:
        """Return deterministic strongly-connected circular dependency groups."""

        groups = [
            sorted(group)
            for group in nx.strongly_connected_components(graph)
            if len(group) > 1
        ]
        return sorted(groups)

    def calculate_degrees(
        self,
        graph: nx.DiGraph,
    ) -> dict[str, tuple[int, int]]:
        """Return ``(fan_in, fan_out)`` for every graph node."""

        return {
            name: (graph.in_degree(name), graph.out_degree(name))
            for name in sorted(graph.nodes)
        }


def module_name_for_path(project_root: str | Path, file_path: str | Path) -> str:
    """Convert a project-relative Python path to its importable module name."""

    root = Path(project_root)
    relative = Path(file_path).relative_to(root)
    parts = list(relative.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts) if parts else root.name


def resolve_internal_imports(
    importing_module: str,
    imports: list[str],
    from_imports: list[str],
    module_names: set[str],
) -> list[str]:
    """Resolve raw import strings to the longest matching internal modules."""

    resolved: set[str] = set()
    candidates_by_length = sorted(
        module_names,
        key=lambda name: (-len(name.split(".")), name),
    )
    for raw_import in [*imports, *from_imports]:
        candidate = _absolute_candidate(importing_module, raw_import, module_names)
        if not candidate:
            continue
        for module_name in candidates_by_length:
            if candidate == module_name or candidate.startswith(f"{module_name}."):
                resolved.add(module_name)
                break
    return sorted(resolved)


def _absolute_candidate(
    importing_module: str,
    raw_import: str,
    module_names: set[str],
) -> str:
    if not raw_import.startswith("."):
        return raw_import

    level = len(raw_import) - len(raw_import.lstrip("."))
    suffix = raw_import[level:]
    is_package = any(
        name.startswith(f"{importing_module}.")
        for name in module_names
        if name != importing_module
    )
    package = importing_module if is_package else importing_module.rpartition(".")[0]
    package_parts = package.split(".") if package else []
    levels_to_remove = level - 1
    if levels_to_remove > len(package_parts):
        return ""
    base_parts = package_parts[: len(package_parts) - levels_to_remove]
    suffix_parts = suffix.split(".") if suffix else []
    return ".".join([*base_parts, *suffix_parts])
