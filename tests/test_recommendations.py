import pytest

from analyzer.recommendations import RecommendationEngine
from models import FunctionMetrics, ModuleMetrics


def function_metric(**changes) -> FunctionMetrics:
    values = {
        "name": "function",
        "qualified_name": "function",
        "file_path": "module.py",
        "start_line": 10,
        "end_line": 30,
        "lines": 20,
        "parameters": 2,
        "complexity": 3,
        "nesting_depth": 1,
        "branches": 1,
        "loops": 0,
        "try_blocks": 0,
        "returns": 1,
        "calls": 1,
        "local_variables": 1,
        "nested_functions": 0,
    }
    values.update(changes)
    return FunctionMetrics(**values)


def module_metric(**changes) -> ModuleMetrics:
    values = {
        "name": "module",
        "file_path": "module.py",
        "lines": 100,
        "function_count": 2,
        "class_count": 0,
        "internal_imports": [],
        "external_imports": [],
        "fan_in": 1,
        "fan_out": 1,
        "maintainability_index": 90.0,
        "average_function_complexity": 3.0,
        "max_function_complexity": 5,
        "max_function_score": 15.0,
        "circular_dependency_count": 0,
    }
    values.update(changes)
    return ModuleMetrics(**values)


@pytest.mark.parametrize(
    ("changes", "issue_type", "metric_value", "threshold"),
    [
        ({"lines": 61}, "large_function", 61, 60),
        ({"nesting_depth": 5}, "deep_nesting", 5, 5),
        ({"complexity": 16}, "high_complexity", 16, 15),
        ({"parameters": 8}, "too_many_parameters", 8, 7),
    ],
)
def test_function_rules_trigger_at_required_boundaries(
    changes,
    issue_type: str,
    metric_value: float,
    threshold: float,
) -> None:
    issues = RecommendationEngine().for_function(function_metric(**changes))
    issue = next(item for item in issues if item.issue_type == issue_type)

    assert issue.metric_value == metric_value
    assert issue.threshold == threshold
    assert issue.symbol_name == "function"
    assert issue.line_number == 10


def test_function_rules_do_not_trigger_at_non_exceeding_boundaries() -> None:
    issues = RecommendationEngine().for_function(
        function_metric(lines=60, nesting_depth=4, complexity=15, parameters=7)
    )

    assert issues == []


def test_high_fan_out_rule_uses_configured_threshold() -> None:
    engine = RecommendationEngine(fan_out_threshold=5)

    assert engine.for_module(module_metric(fan_out=5)) == []
    issue = engine.for_module(module_metric(fan_out=6))[0]
    assert issue.issue_type == "high_fan_out"
    assert issue.metric_value == 6
    assert issue.threshold == 5


def test_cycle_rule_returns_one_advisory_issue_per_group() -> None:
    issues = RecommendationEngine().for_cycles([["b", "a"], ["d", "c"]])

    assert [issue.symbol_name for issue in issues] == ["a -> b -> a", "c -> d -> c"]
    assert all(issue.issue_type == "circular_dependency" for issue in issues)


def test_recommendation_language_is_advisory_not_insulting() -> None:
    engine = RecommendationEngine(fan_out_threshold=2)
    issues = engine.for_function(
        function_metric(lines=100, nesting_depth=7, complexity=25, parameters=10)
    )
    issues += engine.for_module(module_metric(fan_out=5))
    issues += engine.for_cycles([["a", "b"]])

    combined = " ".join(issue.message.lower() for issue in issues)
    assert "bad" not in combined
    assert "must" not in combined
    assert all(issue.message.startswith(("Consider", "This module")) for issue in issues)
