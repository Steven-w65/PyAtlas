from analyzer.metric_calculator import MetricCalculator
from models import ClassMetrics, FunctionMetrics


def function_metric(name: str, complexity: int, score: float) -> FunctionMetrics:
    return FunctionMetrics(
        name=name,
        qualified_name=name,
        file_path="module.py",
        start_line=1,
        end_line=10,
        lines=10,
        parameters=1,
        complexity=complexity,
        nesting_depth=1,
        branches=1,
        loops=0,
        try_blocks=0,
        returns=1,
        calls=1,
        local_variables=1,
        nested_functions=0,
        confusion_score=score,
    )


def test_calculate_module_metrics_combines_precomputed_values() -> None:
    functions = [function_metric("low", 2, 10), function_metric("high", 8, 60)]
    classes = [
        ClassMetrics(
            name="Worker",
            qualified_name="Worker",
            file_path="module.py",
            start_line=1,
            end_line=20,
            lines=20,
            method_count=2,
            average_method_complexity=5,
            max_method_complexity=8,
        )
    ]

    metrics = MetricCalculator().calculate_module_metrics(
        module_name="package.module",
        file_path="module.py",
        source="first = 1\n\nsecond = 2\nthird = 3\n",
        functions=functions,
        classes=classes,
        internal_imports=["package.helpers", "package.helpers"],
        external_imports=["requests", "os"],
        fan_in=3,
        fan_out=2,
        maintainability_index=72.5,
        circular_dependency_count=1,
    )

    assert metrics.name == "package.module"
    assert metrics.lines == 3
    assert (metrics.function_count, metrics.class_count) == (2, 1)
    assert metrics.internal_imports == ["package.helpers"]
    assert metrics.external_imports == ["os", "requests"]
    assert (metrics.fan_in, metrics.fan_out) == (3, 2)
    assert metrics.maintainability_index == 72.5
    assert metrics.average_function_complexity == 5
    assert metrics.max_function_complexity == 8
    assert metrics.max_function_score == 60
    assert metrics.circular_dependency_count == 1


def test_calculate_module_metrics_uses_zero_safe_aggregates() -> None:
    metrics = MetricCalculator().calculate_module_metrics(
        module_name="empty",
        file_path="empty.py",
        source="",
        functions=[],
        classes=[],
        internal_imports=[],
        external_imports=[],
        fan_in=0,
        fan_out=0,
        maintainability_index=None,
        circular_dependency_count=0,
    )

    assert metrics.lines == 0
    assert metrics.average_function_complexity == 0
    assert metrics.max_function_complexity == 0
    assert metrics.max_function_score == 0

