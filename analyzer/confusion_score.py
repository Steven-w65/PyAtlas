"""Explainable heuristic maintainability-risk scoring."""

from __future__ import annotations

from collections.abc import Iterable

from models import ClassMetrics, FunctionMetrics, ModuleMetrics, ScoreContribution


FUNCTION_RULES = (
    ("Cyclomatic Complexity", "complexity", 5.0, 25.0, 0.25),
    ("Function Length", "lines", 20.0, 120.0, 0.20),
    ("Nesting Depth", "nesting_depth", 2.0, 7.0, 0.20),
    ("Parameter Count", "parameters", 4.0, 10.0, 0.10),
    ("Branches", "branches", 4.0, 20.0, 0.10),
    ("Local Variables", "local_variables", 8.0, 30.0, 0.05),
    ("Function Calls", "calls", 8.0, 35.0, 0.05),
    ("Nested Functions", "nested_functions", 0.0, 4.0, 0.05),
)


def capped_ratio(value: float, concern_start: float, high_risk: float) -> float:
    """Normalize a raw value to 0–100 between two risk thresholds."""

    if value <= concern_start:
        return 0.0
    if value >= high_risk:
        return 100.0
    return ((value - concern_start) / (high_risk - concern_start)) * 100.0


class ConfusionScorer:
    """Calculate bounded scores and retain every metric contribution."""

    def score_function(
        self,
        metrics: FunctionMetrics,
    ) -> tuple[float, list[ScoreContribution]]:
        contributions = [
            _contribution(
                label,
                float(getattr(metrics, attribute)),
                concern,
                high_risk,
                weight,
            )
            for label, attribute, concern, high_risk, weight in FUNCTION_RULES
        ]
        return _score(contributions), contributions

    def score_class(
        self,
        metrics: ClassMetrics,
    ) -> tuple[float, list[ScoreContribution]]:
        contributions = [
            _contribution(
                "Average Method Complexity",
                metrics.average_method_complexity,
                3.0,
                20.0,
                0.45,
            ),
            _contribution(
                "Maximum Method Complexity",
                float(metrics.max_method_complexity),
                5.0,
                25.0,
                0.35,
            ),
            _contribution("Class Length", float(metrics.lines), 80.0, 500.0, 0.20),
        ]
        return _score(contributions), contributions

    def score_module(
        self,
        metrics: ModuleMetrics,
    ) -> tuple[float, list[ScoreContribution]]:
        maintainability_risk = (
            0.0
            if metrics.maintainability_index is None
            else 100.0 - metrics.maintainability_index
        )
        class_complexity_proxy = (
            float(metrics.max_function_complexity) if metrics.class_count else 0.0
        )
        contributions = [
            _contribution(
                "Average Function Complexity",
                metrics.average_function_complexity,
                5.0,
                20.0,
                0.20,
            ),
            _contribution(
                "Largest Function Risk",
                metrics.max_function_score,
                20.0,
                80.0,
                0.15,
            ),
            _contribution("Module Length", float(metrics.lines), 200.0, 1500.0, 0.10),
            _contribution("Fan-Out", float(metrics.fan_out), 3.0, 15.0, 0.10),
            _contribution("Fan-In", float(metrics.fan_in), 5.0, 30.0, 0.10),
            _contribution(
                "Circular Dependencies",
                float(metrics.circular_dependency_count),
                0.0,
                3.0,
                0.15,
            ),
            _contribution(
                "Maintainability Risk",
                maintainability_risk,
                20.0,
                80.0,
                0.10,
            ),
            _contribution(
                "Class Complexity",
                class_complexity_proxy,
                5.0,
                25.0,
                0.10,
            ),
        ]
        return _score(contributions), contributions

    def score_project(
        self,
        modules: list[ModuleMetrics],
        cycles: list[list[str]],
    ) -> float:
        if not modules:
            return 0.0
        loc_weights = [min(max(module.lines, 1), 1000) for module in modules]
        weighted_average = sum(
            module.confusion_score * weight
            for module, weight in zip(modules, loc_weights, strict=True)
        ) / sum(loc_weights)
        hotspot_risk = (
            sum(module.confusion_score > 80 for module in modules)
            / len(modules)
            * 100.0
        )
        cycle_risk = capped_ratio(float(len(cycles)), 0.0, 5.0)
        return _clamp(round(
            weighted_average * 0.70 + hotspot_risk * 0.20 + cycle_risk * 0.10,
            2,
        ))


def _contribution(
    metric: str,
    raw_value: float,
    concern_start: float,
    high_risk: float,
    weight: float,
) -> ScoreContribution:
    normalized = capped_ratio(raw_value, concern_start, high_risk)
    points = round(normalized * weight, 4)
    reason = (
        f"{metric} is {raw_value:g}; risk begins above {concern_start:g} "
        f"and reaches the cap at {high_risk:g}."
    )
    return ScoreContribution(
        metric=metric,
        raw_value=raw_value,
        normalized_value=round(normalized, 4),
        weight=weight,
        points=points,
        reason=reason,
    )


def _score(contributions: Iterable[ScoreContribution]) -> float:
    return _clamp(round(sum(item.points for item in contributions), 2))


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))
