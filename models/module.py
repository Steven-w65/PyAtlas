"""Module-level analysis contracts."""

from dataclasses import dataclass, field

from models.function_info import ScoreContribution


@dataclass
class ModuleMetrics:
    name: str
    file_path: str
    lines: int
    function_count: int
    class_count: int
    internal_imports: list[str]
    external_imports: list[str]
    fan_in: int
    fan_out: int
    maintainability_index: float | None
    average_function_complexity: float
    max_function_complexity: int
    max_function_score: float
    circular_dependency_count: int
    confusion_score: float = 0.0
    score_contributions: list[ScoreContribution] = field(default_factory=list)

