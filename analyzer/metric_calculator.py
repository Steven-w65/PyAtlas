"""Aggregation of previously extracted values into module metrics."""

from __future__ import annotations

from models import ClassMetrics, FunctionMetrics, ModuleMetrics


class MetricCalculator:
    """Combine source and analyzer outputs without rescanning or reparsing."""

    def calculate_module_metrics(
        self,
        module_name: str,
        file_path: str,
        source: str,
        functions: list[FunctionMetrics],
        classes: list[ClassMetrics],
        internal_imports: list[str],
        external_imports: list[str],
        fan_in: int,
        fan_out: int,
        maintainability_index: float | None,
        circular_dependency_count: int,
    ) -> ModuleMetrics:
        """Return one module metric record from precomputed inputs."""

        complexities = [function.complexity for function in functions]
        scores = [function.confusion_score for function in functions]
        nonblank_lines = sum(bool(line.strip()) for line in source.splitlines())
        return ModuleMetrics(
            name=module_name,
            file_path=file_path,
            lines=nonblank_lines,
            function_count=len(functions),
            class_count=len(classes),
            internal_imports=sorted(set(internal_imports)),
            external_imports=sorted(set(external_imports)),
            fan_in=fan_in,
            fan_out=fan_out,
            maintainability_index=maintainability_index,
            average_function_complexity=(
                round(sum(complexities) / len(complexities), 2)
                if complexities
                else 0.0
            ),
            max_function_complexity=max(complexities, default=0),
            max_function_score=max(scores, default=0.0),
            circular_dependency_count=circular_dependency_count,
        )

