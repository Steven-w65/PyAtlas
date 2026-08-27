"""AST-based symbol and structural metric extraction."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from models import ClassMetrics, FunctionMetrics


_FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)
_NESTING_NODES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.Try,
    ast.TryStar,
    ast.With,
    ast.AsyncWith,
    ast.Match,
)


class ASTAnalyzer:
    """Extract typed metrics and import metadata from one source string."""

    def analyze_file(
        self,
        file_path: str | Path,
        source: str,
    ) -> tuple[list[FunctionMetrics], list[ClassMetrics], dict[str, Any]]:
        """Analyze *source* without allowing syntax errors to escape."""

        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as exc:
            message = f"{file_path}:{exc.lineno or '?'}: SyntaxError: {exc.msg}"
            return [], [], {
                "imports": [],
                "from_imports": [],
                "syntax_error": message,
            }

        visitor = _SymbolVisitor(str(file_path))
        visitor.visit(tree)
        return visitor.functions, visitor.classes, {
            "imports": sorted(visitor.imports),
            "from_imports": sorted(visitor.from_imports),
            "syntax_error": None,
        }


class _SymbolVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.name_stack: list[str] = []
        self.functions: list[FunctionMetrics] = []
        self.classes: list[ClassMetrics] = []
        self.imports: set[str] = set()
        self.from_imports: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        self.imports.update(alias.name for alias in node.names)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        prefix = "." * node.level + (node.module or "")
        for alias in node.names:
            separator = "." if prefix and not prefix.endswith(".") else ""
            self.from_imports.add(f"{prefix}{separator}{alias.name}")

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        qualified_name = self._qualified(node.name)
        method_count = sum(isinstance(child, _FUNCTION_NODES) for child in node.body)
        self.classes.append(
            ClassMetrics(
                name=node.name,
                qualified_name=qualified_name,
                file_path=self.file_path,
                start_line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                lines=getattr(node, "end_lineno", node.lineno) - node.lineno + 1,
                method_count=method_count,
                average_method_complexity=1.0 if method_count else 0.0,
                max_method_complexity=1 if method_count else 0,
            )
        )
        self.name_stack.append(node.name)
        for child in node.body:
            self.visit(child)
        self.name_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        counter = _FunctionCounter()
        for child in node.body:
            counter.visit(child)

        end_line = getattr(node, "end_lineno", node.lineno)
        self.functions.append(
            FunctionMetrics(
                name=node.name,
                qualified_name=self._qualified(node.name),
                file_path=self.file_path,
                start_line=node.lineno,
                end_line=end_line,
                lines=end_line - node.lineno + 1,
                parameters=_parameter_count(node.args),
                complexity=1,
                nesting_depth=_maximum_nesting(node.body),
                branches=counter.branches,
                loops=counter.loops,
                try_blocks=counter.try_blocks,
                returns=counter.returns,
                calls=counter.calls,
                local_variables=len(counter.local_variables),
                nested_functions=counter.nested_functions,
            )
        )

        self.name_stack.append(node.name)
        for child in node.body:
            self.visit(child)
        self.name_stack.pop()

    def _qualified(self, name: str) -> str:
        return ".".join([*self.name_stack, name])


class _FunctionCounter(ast.NodeVisitor):
    def __init__(self) -> None:
        self.branches = 0
        self.loops = 0
        self.try_blocks = 0
        self.returns = 0
        self.calls = 0
        self.local_variables: set[str] = set()
        self.nested_functions = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.nested_functions += 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.nested_functions += 1

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return

    def visit_If(self, node: ast.If) -> None:
        self.branches += 1
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.branches += 1
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        self.branches += len(node.cases)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.loops += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.loops += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.loops += 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self.try_blocks += 1
        self.generic_visit(node)

    def visit_TryStar(self, node: ast.TryStar) -> None:
        self.try_blocks += 1
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        self.returns += 1
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        self.calls += 1
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self.local_variables.update(_assigned_names(target))
        self.generic_visit(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.local_variables.update(_assigned_names(node.target))
        if node.value is not None:
            self.visit(node.value)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.local_variables.update(_assigned_names(node.target))
        self.visit(node.value)


def _assigned_names(node: ast.AST) -> set[str]:
    return {
        child.id
        for child in ast.walk(node)
        if isinstance(child, ast.Name)
    }


def _parameter_count(arguments: ast.arguments) -> int:
    count = len(arguments.posonlyargs) + len(arguments.args) + len(arguments.kwonlyargs)
    return count + int(arguments.vararg is not None) + int(arguments.kwarg is not None)


def _maximum_nesting(nodes: list[ast.stmt]) -> int:
    def depth(node: ast.AST, current: int) -> int:
        next_depth = current + 1 if isinstance(node, _NESTING_NODES) else current
        maximum = next_depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, _FUNCTION_NODES + (ast.ClassDef,)):
                continue
            maximum = max(maximum, depth(child, next_depth))
        return maximum

    return max((depth(node, 0) for node in nodes), default=0)
