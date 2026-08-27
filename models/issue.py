"""Maintainability issue contracts."""

from dataclasses import dataclass


@dataclass
class CodeIssue:
    issue_type: str
    severity: str
    message: str
    file_path: str
    symbol_name: str | None = None
    line_number: int | None = None
    metric_value: float | None = None
    threshold: float | None = None

