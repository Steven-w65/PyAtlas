from pathlib import Path

from analyzer.dependency_analyzer import (
    DependencyAnalyzer,
    module_name_for_path,
    resolve_internal_imports,
)


def test_internal_imports_create_edges_and_external_imports_do_not() -> None:
    graph = DependencyAnalyzer().build_graph(
        {"app", "helpers", "isolated"},
        {"app": ["helpers", "requests"], "helpers": []},
    )

    assert sorted(graph.nodes) == ["app", "helpers", "isolated"]
    assert sorted(graph.edges) == [("app", "helpers")]


def test_calculate_degrees_returns_fan_in_then_fan_out() -> None:
    analyzer = DependencyAnalyzer()
    graph = analyzer.build_graph(
        {"a", "b", "c"},
        {"a": ["b", "c"], "b": ["a"], "c": []},
    )

    assert analyzer.calculate_degrees(graph) == {
        "a": (1, 2),
        "b": (1, 1),
        "c": (1, 0),
    }


def test_find_cycles_returns_stable_groups() -> None:
    analyzer = DependencyAnalyzer()
    graph = analyzer.build_graph(
        {"a", "b", "c", "d"},
        {"a": ["b"], "b": ["c"], "c": ["a"], "d": []},
    )

    assert analyzer.find_cycles(graph) == [["a", "b", "c"]]


def test_module_name_resolves_packages_and_regular_modules(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    package.mkdir()

    assert module_name_for_path(tmp_path, package / "__init__.py") == "pkg"
    assert module_name_for_path(tmp_path, package / "api.py") == "pkg.api"
    assert module_name_for_path(tmp_path, tmp_path / "main.py") == "main"


def test_resolve_internal_imports_uses_longest_module_prefix() -> None:
    modules = {"pkg", "pkg.api", "pkg.helpers", "pkg.helpers.formatting"}

    resolved = resolve_internal_imports(
        "pkg.api",
        ["os", "pkg.helpers.formatting.tools"],
        ["requests.Session", "pkg.helpers.render"],
        modules,
    )

    assert resolved == ["pkg.helpers", "pkg.helpers.formatting"]


def test_resolve_relative_imports_from_module_and_package() -> None:
    modules = {"pkg", "pkg.api", "pkg.helpers", "pkg.sub", "pkg.sub.worker"}

    from_module = resolve_internal_imports(
        "pkg.api",
        [],
        [".helpers.run"],
        modules,
    )
    from_package = resolve_internal_imports(
        "pkg.sub",
        [],
        [".worker.run", "..helpers.run"],
        modules,
    )

    assert from_module == ["pkg.helpers"]
    assert from_package == ["pkg.helpers", "pkg.sub.worker"]
