import pytest

from analyzer.confusion_score import ConfusionScorer
from models import ClassMetrics, FunctionMetrics, ModuleMetrics


def function_metric(**changes) -> FunctionMetrics:
    values = {
        "name": "function",
        "qualified_name": "function",
        "file_path": "module.py",
        "start_line": 1,
        "end_line": 10,
        "lines": 10,
        "parameters": 1,
        "complexity": 2,
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


def class_metric(**changes) -> ClassMetrics:
    values = {
        "name": "Worker",
        "qualified_name": "Worker",
        "file_path": "module.py",
        "start_line": 1,
        "end_line": 40,
        "lines": 40,
        "method_count": 3,
        "average_method_complexity": 3.0,
        "max_method_complexity": 5,
    }
    values.update(changes)
    return ClassMetrics(**values)


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


def test_function_scores_remain_bounded_and_contributions_reconcile() -> None:
    score, contributions = ConfusionScorer().score_function(
        function_metric(
            lines=500,
            complexity=100,
            nesting_depth=20,
            parameters=30,
            branches=50,
            local_variables=80,
            calls=80,
            nested_functions=10,
        )
    )

    assert score == 100
    assert sum(item.points for item in contributions) == pytest.approx(score, abs=0.01)
    assert {item.metric for item in contributions} == {
        "Cyclomatic Complexity",
        "Function Length",
        "Nesting Depth",
        "Parameter Count",
        "Branches",
        "Local Variables",
        "Function Calls",
        "Nested Functions",
    }


def test_complexity_nesting_and_length_each_increase_function_score() -> None:
    scorer = ConfusionScorer()
    baseline, _ = scorer.score_function(function_metric())
    complex_score, _ = scorer.score_function(function_metric(complexity=20))
    nested_score, _ = scorer.score_function(function_metric(nesting_depth=6))
    long_score, _ = scorer.score_function(function_metric(lines=100, end_line=100))

    assert complex_score > baseline
    assert nested_score > baseline
    assert long_score > baseline


def test_clearly_high_risk_function_scores_above_low_risk_function() -> None:
    scorer = ConfusionScorer()
    low, _ = scorer.score_function(function_metric())
    high, _ = scorer.score_function(
        function_metric(
            lines=130,
            end_line=130,
            complexity=25,
            nesting_depth=7,
            parameters=10,
            branches=20,
        )
    )

    assert low < high


def test_class_and_module_scores_include_explanations_and_are_bounded() -> None:
    scorer = ConfusionScorer()
    class_score, class_contributions = scorer.score_class(
        class_metric(lines=600, average_method_complexity=25, max_method_complexity=40)
    )
    module_score, module_contributions = scorer.score_module(
        module_metric(
            lines=3000,
            fan_in=40,
            fan_out=20,
            maintainability_index=10,
            average_function_complexity=25,
            max_function_complexity=30,
            max_function_score=95,
            circular_dependency_count=4,
            class_count=2,
        )
    )

    assert 0 <= class_score <= 100
    assert 0 <= module_score <= 100
    assert sum(item.points for item in class_contributions) == pytest.approx(class_score, abs=0.01)
    assert sum(item.points for item in module_contributions) == pytest.approx(module_score, abs=0.01)


def test_module_size_alone_does_not_make_a_module_high_risk() -> None:
    score, _ = ConfusionScorer().score_module(module_metric(lines=5000))

    assert score < 40


def test_project_score_increases_with_hotspots_and_cycles() -> None:
    scorer = ConfusionScorer()
    calm = [module_metric(name=f"calm_{index}", confusion_score=20) for index in range(4)]
    hot = [module_metric(name=f"hot_{index}", confusion_score=90) for index in range(4)]

    calm_score = scorer.score_project(calm, [])
    hot_score = scorer.score_project(hot, [])
    cyclic_score = scorer.score_project(calm, [["calm_0", "calm_1"]])

    assert 0 <= calm_score < hot_score <= 100
    assert cyclic_score > calm_score
