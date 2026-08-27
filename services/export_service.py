"""Serialization of completed PyAtlas analysis results."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict

from models import ProjectAnalysis


HOTSPOT_COLUMNS = [
    "Name",
    "Type",
    "File",
    "Confusion Score",
    "Complexity",
    "Lines",
    "Nesting",
    "Issues",
]


class ExportService:
    """Convert analysis models to stable user-download formats."""

    def to_json(self, analysis: ProjectAnalysis) -> str:
        """Return formatted JSON containing only standard serializable values."""

        return json.dumps(
            asdict(analysis),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )

    def hotspot_csv(self, analysis: ProjectAnalysis) -> str:
        """Return function and module hotspots aligned with the dashboard table."""

        rows: list[dict[str, str | int]] = []
        for module in analysis.modules:
            rows.append(
                {
                    "Name": module.name,
                    "Type": "Module",
                    "File": module.file_path,
                    "Confusion Score": f"{module.confusion_score:.2f}",
                    "Complexity": f"{module.average_function_complexity:.2f}",
                    "Lines": module.lines,
                    "Nesting": "",
                    "Issues": self._issue_count(
                        analysis,
                        module.file_path,
                        module.name,
                    ),
                }
            )
        for function in analysis.functions:
            rows.append(
                {
                    "Name": function.qualified_name,
                    "Type": "Function",
                    "File": function.file_path,
                    "Confusion Score": f"{function.confusion_score:.2f}",
                    "Complexity": function.complexity,
                    "Lines": function.lines,
                    "Nesting": function.nesting_depth,
                    "Issues": self._issue_count(
                        analysis,
                        function.file_path,
                        function.qualified_name,
                    ),
                }
            )
        rows.sort(
            key=lambda row: (
                -float(row["Confusion Score"]),
                str(row["Type"]),
                str(row["Name"]),
            )
        )

        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=HOTSPOT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue()

    @staticmethod
    def _issue_count(
        analysis: ProjectAnalysis,
        file_path: str,
        symbol_name: str,
    ) -> int:
        return sum(
            issue.file_path == file_path and issue.symbol_name == symbol_name
            for issue in analysis.issues
        )

