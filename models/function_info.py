"""Function-level analysis contracts."""

from dataclasses import dataclass, field


@dataclass
class ScoreContribution:
    metric: str
    raw_value: float
    normalized_value: float
    weight: float
    points: float
    reason: str


@dataclass
class FunctionMetrics:
    name: str
    qualified_name: str
    file_path: str
    start_line: int
    end_line: int
    lines: int
    parameters: int
    complexity: int
    nesting_depth: int
    branches: int
    loops: int
    try_blocks: int
    returns: int
    calls: int
    local_variables: int
    nested_functions: int
    confusion_score: float = 0.0
    score_contributions: list[ScoreContribution] = field(default_factory=list)

