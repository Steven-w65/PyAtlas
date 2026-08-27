"""End-to-end orchestration for local Python project analysis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from analyzer.ast_analyzer import ASTAnalyzer
from analyzer.complexity_analyzer import ComplexityAnalyzer
from analyzer.confusion_score import ConfusionScorer
from analyzer.dependency_analyzer import (
    DependencyAnalyzer,
    module_name_for_path,
    resolve_internal_imports,
)
from analyzer.metric_calculator import MetricCalculator
from analyzer.project_scanner import ProjectScanner
from analyzer.recommendations import RecommendationEngine
from models import ClassMetrics, CodeIssue, FunctionMetrics, ModuleMetrics, ProjectAnalysis


@dataclass
class _AnalyzedFile:
    module_name: str
    path: Path
    source: str
    functions: list[FunctionMetrics]
    classes: list[ClassMetrics]
    metadata: dict[str, Any]
    maintainability_index: float | None


class AnalysisService:
    """Run all PyAtlas analyzers and return one complete project result."""

    def __init__(self) -> None:
        self.ast_analyzer = ASTAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.metric_calculator = MetricCalculator()
        self.scorer = ConfusionScorer()
        self.recommendations = RecommendationEngine()

    def analyze_project(
        self,
        project_path: str | Path,
        extra_ignore_patterns: list[str] | None = None,
    ) -> ProjectAnalysis:
        """Analyze a local Python project while isolating file-level failures."""

        root = Path(project_path)
        scanner = ProjectScanner(extra_ignore_patterns=extra_ignore_patterns)
        paths = scanner.scan(root)
        errors = list(scanner.errors)
        sources, read_errors = self._read_sources(paths)
        errors.extend(read_errors)

        module_by_path = {
            path: module_name_for_path(root, path)
            for path in paths
        }
        module_names = set(module_by_path.values())
        analyzed: dict[str, _AnalyzedFile] = {}
        for path in paths:
            if path not in sources:
                continue
            module_name = module_by_path[path]
            try:
                analyzed_file = self._analyze_file(module_name, path, sources[path])
            except Exception as exc:  # isolate unexpected analyzer failures per file
                errors.append(self._format_error(path, exc))
                continue
            syntax_error = analyzed_file.metadata.get("syntax_error")
            if syntax_error:
                errors.append(str(syntax_error))
            analyzed[module_name] = analyzed_file

        internal_by_module: dict[str, list[str]] = {}
        external_by_module: dict[str, list[str]] = {}
        for module_name, item in analyzed.items():
            raw_imports = list(item.metadata["imports"])
            raw_from_imports = list(item.metadata["from_imports"])
            internal = resolve_internal_imports(
                module_name,
                raw_imports,
                raw_from_imports,
                module_names,
            )
            internal_by_module[module_name] = [
                dependency for dependency in internal if dependency != module_name
            ]
            external_by_module[module_name] = self._external_imports(
                module_name,
                raw_imports,
                raw_from_imports,
                module_names,
            )

        graph = self.dependency_analyzer.build_graph(module_names, internal_by_module)
        degrees = self.dependency_analyzer.calculate_degrees(graph)
        cycles = self.dependency_analyzer.find_cycles(graph)
        cycle_count = {
            module_name: sum(module_name in cycle for cycle in cycles)
            for module_name in module_names
        }

        modules: list[ModuleMetrics] = []
        for module_name in sorted(analyzed):
            item = analyzed[module_name]
            fan_in, fan_out = degrees.get(module_name, (0, 0))
            module = self.metric_calculator.calculate_module_metrics(
                module_name=module_name,
                file_path=str(item.path),
                source=item.source,
                functions=item.functions,
                classes=item.classes,
                internal_imports=internal_by_module[module_name],
                external_imports=external_by_module[module_name],
                fan_in=fan_in,
                fan_out=fan_out,
                maintainability_index=item.maintainability_index,
                circular_dependency_count=cycle_count[module_name],
            )
            module.confusion_score, module.score_contributions = self.scorer.score_module(module)
            modules.append(module)

        functions = sorted(
            (function for item in analyzed.values() for function in item.functions),
            key=lambda metric: (metric.file_path, metric.start_line, metric.qualified_name),
        )
        classes = sorted(
            (class_metric for item in analyzed.values() for class_metric in item.classes),
            key=lambda metric: (metric.file_path, metric.start_line, metric.qualified_name),
        )
        issues = self._issues(functions, modules, cycles)
        project_score = self.scorer.score_project(modules, cycles)
        return ProjectAnalysis(
            project_name=root.name,
            project_path=str(root.resolve()),
            python_file_count=len(paths),
            total_lines=sum(module.lines for module in modules),
            function_count=len(functions),
            class_count=len(classes),
            project_confusion_score=project_score,
            modules=modules,
            functions=functions,
            classes=classes,
            issues=issues,
            dependency_edges=sorted(graph.edges()),
            circular_dependencies=cycles,
            errors=sorted(set(errors)),
        )

    def _read_sources(
        self,
        paths: list[Path],
    ) -> tuple[dict[Path, str], list[str]]:
        sources: dict[Path, str] = {}
        errors: list[str] = []
        for path in paths:
            try:
                sources[path] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append(self._format_error(path, exc))
        return sources, errors

    def _analyze_file(self, module_name: str, path: Path, source: str) -> _AnalyzedFile:
        functions, classes, metadata = self.ast_analyzer.analyze_file(path, source)
        complexities = self.complexity_analyzer.function_complexities(source)
        self._apply_complexities(functions, complexities)
        self._update_class_complexities(classes, functions)
        for function in functions:
            function.confusion_score, function.score_contributions = (
                self.scorer.score_function(function)
            )
        for class_metric in classes:
            class_metric.confusion_score, class_metric.score_contributions = (
                self.scorer.score_class(class_metric)
            )
        return _AnalyzedFile(
            module_name=module_name,
            path=path,
            source=source,
            functions=functions,
            classes=classes,
            metadata=metadata,
            maintainability_index=self.complexity_analyzer.maintainability_index(source),
        )

    @staticmethod
    def _apply_complexities(
        functions: list[FunctionMetrics],
        complexities: dict[str, int],
    ) -> None:
        for function in functions:
            if function.qualified_name in complexities:
                function.complexity = complexities[function.qualified_name]
                continue
            matching = [
                value
                for name, value in complexities.items()
                if name == function.name or name.endswith(f".{function.qualified_name}")
            ]
            if len(matching) == 1:
                function.complexity = matching[0]

    @staticmethod
    def _update_class_complexities(
        classes: list[ClassMetrics],
        functions: list[FunctionMetrics],
    ) -> None:
        for class_metric in classes:
            prefix = f"{class_metric.qualified_name}."
            method_complexities = [
                function.complexity
                for function in functions
                if function.qualified_name.startswith(prefix)
            ]
            if method_complexities:
                class_metric.average_method_complexity = round(
                    sum(method_complexities) / len(method_complexities),
                    2,
                )
                class_metric.max_method_complexity = max(method_complexities)

    @staticmethod
    def _external_imports(
        importing_module: str,
        imports: list[str],
        from_imports: list[str],
        module_names: set[str],
    ) -> list[str]:
        external: set[str] = set()
        for raw_import in [*imports, *from_imports]:
            if raw_import.startswith("."):
                continue
            internal = resolve_internal_imports(
                importing_module,
                [raw_import],
                [],
                module_names,
            )
            if not internal:
                external.add(raw_import.split(".", 1)[0])
        return sorted(external)

    def _issues(
        self,
        functions: list[FunctionMetrics],
        modules: list[ModuleMetrics],
        cycles: list[list[str]],
    ) -> list[CodeIssue]:
        issues = [
            issue
            for function in functions
            for issue in self.recommendations.for_function(function)
        ]
        issues.extend(
            issue
            for module in modules
            for issue in self.recommendations.for_module(module)
        )
        issues.extend(self.recommendations.for_cycles(cycles))
        severity = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        return sorted(
            issues,
            key=lambda issue: (
                severity[issue.severity],
                issue.file_path,
                issue.symbol_name or "",
                issue.issue_type,
            ),
        )

    @staticmethod
    def _format_error(path: Path, exc: Exception) -> str:
        return f"{path}: {type(exc).__name__}: {exc}"
