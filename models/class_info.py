"""Class-level analysis contracts."""

from dataclasses import dataclass, field

from models.function_info import ScoreContribution


@dataclass
class ClassMetrics:
    name: str
    qualified_name: str
    file_path: str
    start_line: int
    end_line: int
    lines: int
    method_count: int
    average_method_complexity: float
    max_method_complexity: int
    confusion_score: float = 0.0
    score_contributions: list[ScoreContribution] = field(default_factory=list)

