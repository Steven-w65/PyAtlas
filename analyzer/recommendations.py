"""Threshold-based, advisory maintainability recommendations."""

from __future__ import annotations

from models import CodeIssue, FunctionMetrics, ModuleMetrics


_SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


class RecommendationEngine:
    """Generate educational issues from explicit structural thresholds."""

    def __init__(self, fan_out_threshold: int = 8) -> None:
        self.fan_out_threshold = fan_out_threshold

    def for_function(self, metrics: FunctionMetrics) -> list[CodeIssue]:
        """Return recommendations triggered by one function's metrics."""

        issues: list[CodeIssue] = []
        if metrics.lines > 60:
            issues.append(
                self._function_issue(
                    metrics,
                    issue_type="large_function",
                    severity="medium",
                    message=(
                        "Consider splitting this function into smaller units "
                        "representing separate responsibilities."
                    ),
                    metric_value=metrics.lines,
                    threshold=60,
                )
            )
        if metrics.nesting_depth >= 5:
            issues.append(
                self._function_issue(
                    metrics,
                    issue_type="deep_nesting",
                    severity="high",
                    message=(
                        "Consider guard clauses, helper functions, or simplifying "
                        "conditional structure."
                    ),
                    metric_value=metrics.nesting_depth,
                    threshold=5,
                )
            )
        if metrics.complexity > 15:
            issues.append(
                self._function_issue(
                    metrics,
                    issue_type="high_complexity",
                    severity="high",
                    message=(
                        "Consider separating independent decision paths or "
                        "extracting business rules."
                    ),
                    metric_value=metrics.complexity,
                    threshold=15,
                )
            )
        if metrics.parameters > 7:
            issues.append(
                self._function_issue(
                    metrics,
                    issue_type="too_many_parameters",
                    severity="medium",
                    message=(
                        "Consider grouping related parameters into an object or "
                        "configuration structure."
                    ),
                    metric_value=metrics.parameters,
                    threshold=7,
                )
            )
        return _sorted_issues(issues)

    def for_module(self, metrics: ModuleMetrics) -> list[CodeIssue]:
        """Return recommendations triggered by one module's metrics."""

        if metrics.fan_out <= self.fan_out_threshold:
            return []
        return [
            CodeIssue(
                issue_type="high_fan_out",
                severity="medium",
                message=(
                    "This module depends on many internal modules. Review whether "
                    "it is coordinating too many responsibilities."
                ),
                file_path=metrics.file_path,
                symbol_name=metrics.name,
                metric_value=float(metrics.fan_out),
                threshold=float(self.fan_out_threshold),
            )
        ]

    def for_cycles(self, cycles: list[list[str]]) -> list[CodeIssue]:
        """Return one recommendation for each circular dependency group."""

        issues = []
        for cycle in sorted((sorted(group) for group in cycles)):
            route = " -> ".join([*cycle, cycle[0]])
            issues.append(
                CodeIssue(
                    issue_type="circular_dependency",
                    severity="high",
                    message=(
                        "Consider extracting shared responsibilities into a "
                        "separate lower-level module."
                    ),
                    file_path="<dependency-graph>",
                    symbol_name=route,
                    metric_value=float(len(cycle)),
                )
            )
        return issues

    @staticmethod
    def _function_issue(
        metrics: FunctionMetrics,
        *,
        issue_type: str,
        severity: str,
        message: str,
        metric_value: float,
        threshold: float,
    ) -> CodeIssue:
        return CodeIssue(
            issue_type=issue_type,
            severity=severity,
            message=message,
            file_path=metrics.file_path,
            symbol_name=metrics.qualified_name,
            line_number=metrics.start_line,
            metric_value=float(metric_value),
            threshold=float(threshold),
        )


def _sorted_issues(issues: list[CodeIssue]) -> list[CodeIssue]:
    return sorted(
        issues,
        key=lambda issue: (
            _SEVERITY_RANK[issue.severity],
            issue.file_path,
            issue.symbol_name or "",
            issue.issue_type,
        ),
    )
