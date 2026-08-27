"""Radon-backed complexity and maintainability metrics."""

from __future__ import annotations

from radon.complexity import cc_visit
from radon.metrics import mi_visit


class ComplexityAnalyzer:
    """Adapt Radon results to stable PyAtlas data contracts."""

    def function_complexities(self, source: str) -> dict[str, int]:
        """Return cyclomatic complexity keyed by qualified function name."""

        try:
            blocks = cc_visit(source)
        except (SyntaxError, IndentationError, ValueError):
            return {}

        values = {
            getattr(block, "fullname", block.name): int(block.complexity)
            for block in blocks
            if block.__class__.__name__ in {"Function", "Method"}
        }
        return dict(sorted(values.items()))

    def maintainability_index(self, source: str) -> float | None:
        """Return Radon's 0–100 maintainability index, or ``None`` on failure."""

        try:
            value = float(mi_visit(source, multi=True))
        except (SyntaxError, IndentationError, ValueError, ZeroDivisionError):
            return None
        return round(max(0.0, min(100.0, value)), 2)
