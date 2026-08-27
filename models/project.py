"""Aggregate project-analysis contract."""

from dataclasses import dataclass

from models.class_info import ClassMetrics
from models.function_info import FunctionMetrics
from models.issue import CodeIssue
from models.module import ModuleMetrics


@dataclass
class ProjectAnalysis:
    project_name: str
    project_path: str
    python_file_count: int
    total_lines: int
    function_count: int
    class_count: int
    project_confusion_score: float
    modules: list[ModuleMetrics]
    functions: list[FunctionMetrics]
    classes: list[ClassMetrics]
    issues: list[CodeIssue]
    dependency_edges: list[tuple[str, str]]
    circular_dependencies: list[list[str]]
    errors: list[str]

