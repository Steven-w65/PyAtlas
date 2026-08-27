"""Reserved duplicate-function analysis interface."""

from __future__ import annotations

from dataclasses import dataclass

from models import FunctionMetrics


@dataclass
class DuplicateMatch:
    file_a: str
    symbol_a: str
    file_b: str
    symbol_b: str
    similarity: float


class DuplicationAnalyzer:
    """Public boundary reserved for the post-MVP duplicate detector."""

    def compare_functions(
        self,
        functions: list[FunctionMetrics],
        source_by_file: dict[str, str],
        threshold: float = 0.85,
    ) -> list[DuplicateMatch]:
        """Compare normalized functions once duplicate analysis is enabled."""

        raise NotImplementedError("Duplicate detection is deferred from the MVP.")

