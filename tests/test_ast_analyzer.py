from analyzer.ast_analyzer import ASTAnalyzer


SOURCE = """\
import os
from package import helper

class Worker:
    async def run(self, value, flag=False):
        temporary = []
        if flag:
            for item in value:
                if item:
                    temporary.append(helper(item))
        try:
            return temporary
        except ValueError:
            return []

def outer(arg, /, option=True, *values, label=None, **extras):
    def inner():
        return arg
    return inner()
"""


def analyze():
    return ASTAnalyzer().analyze_file("sample.py", SOURCE)


def test_extracts_normal_and_async_functions() -> None:
    functions, _, _ = analyze()

    assert [item.qualified_name for item in functions] == [
        "Worker.run",
        "outer",
        "outer.inner",
    ]


def test_extracts_class_method_and_class_span() -> None:
    _, classes, _ = analyze()

    assert len(classes) == 1
    assert classes[0].qualified_name == "Worker"
    assert classes[0].method_count == 1
    assert classes[0].end_line >= classes[0].start_line


def test_counts_all_parameter_kinds() -> None:
    functions, _, _ = analyze()
    method = next(item for item in functions if item.qualified_name == "Worker.run")
    outer = next(item for item in functions if item.qualified_name == "outer")

    assert method.parameters == 3
    assert outer.parameters == 5


def test_calculates_line_spans() -> None:
    functions, _, _ = analyze()
    method = next(item for item in functions if item.qualified_name == "Worker.run")

    assert method.start_line == 5
    assert method.lines == method.end_line - method.start_line + 1


def test_counts_structural_metrics_without_counting_nested_function_body() -> None:
    functions, _, _ = analyze()
    method = next(item for item in functions if item.qualified_name == "Worker.run")
    outer = next(item for item in functions if item.qualified_name == "outer")

    assert (method.branches, method.loops, method.try_blocks) == (2, 1, 1)
    assert (method.returns, method.calls, method.local_variables) == (2, 2, 1)
    assert outer.returns == 1
    assert outer.calls == 1


def test_calculates_required_maximum_nesting_depth() -> None:
    functions, _, _ = analyze()
    method = next(item for item in functions if item.qualified_name == "Worker.run")

    assert method.nesting_depth == 3


def test_detects_nested_functions() -> None:
    functions, _, _ = analyze()
    outer = next(item for item in functions if item.qualified_name == "outer")
    inner = next(item for item in functions if item.qualified_name == "outer.inner")

    assert outer.nested_functions == 1
    assert inner.nested_functions == 0


def test_extracts_import_metadata_in_stable_order() -> None:
    _, _, metadata = analyze()

    assert metadata["imports"] == ["os"]
    assert metadata["from_imports"] == ["package.helper"]
    assert metadata["syntax_error"] is None


def test_syntax_error_is_reported_without_raising() -> None:
    functions, classes, metadata = ASTAnalyzer().analyze_file(
        "broken.py",
        "def broken(:\n",
    )

    assert functions == []
    assert classes == []
    assert "broken.py:1: SyntaxError" in metadata["syntax_error"]
