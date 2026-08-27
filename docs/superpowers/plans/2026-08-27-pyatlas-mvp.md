# PyAtlas MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete, locally runnable PyAtlas MVP that analyzes Python projects, explains maintainability hotspots, visualizes dependencies, and exports results.

**Architecture:** Typed dataclasses connect focused, Streamlit-free analyzers to one orchestration service. Visualization modules consume completed analysis models, while the Streamlit UI owns only presentation and session state. Work proceeds in test-first vertical slices, with the full suite run at every slice boundary.

**Tech Stack:** Python 3.12+, dataclasses, pathlib, ast, Radon, NetworkX, Plotly, Streamlit, pytest

**Spec:** `docs/superpowers/specs/2026-08-27-pyatlas-mvp-design.md`

## Global Constraints

- Use Python 3.12+.
- Required runtime libraries are `networkx`, `radon`, `streamlit`, and `plotly`; do not add dependencies without a demonstrated feature need.
- Keep all AST, complexity, dependency, metric, scoring, and recommendation logic independent of Streamlit.
- `AnalysisService.analyze_project(project_path, extra_ignore_patterns=None)` is the only analysis entry point used by the UI.
- Preserve the public data contracts and analyzer interfaces from the supplied specification.
- Use deterministic ordering and clamp every confusion score to 0–100.
- Every score must retain explainable `ScoreContribution` records; UI copy must describe scores as heuristic estimates.
- File-level failures must not abort analysis; only an invalid project directory is fatal.
- Core analysis must not require internet access or modify analyzed source code.
- Duplicate detection is deferred, but `analyzer/duplication_analyzer.py` must reserve the specified public interface.
- Write a focused failing test before each behavior, verify the expected failure, add minimal implementation, and rerun targeted plus full tests.

## File responsibility map

- `models/function_info.py`: function metrics and score contributions.
- `models/class_info.py`: class metrics.
- `models/module.py`: module metrics.
- `models/issue.py`: advisory issue contract.
- `models/project.py`: aggregate project result.
- `analyzer/project_scanner.py`: safe deterministic Python-file discovery.
- `analyzer/ast_analyzer.py`: AST-derived symbols, imports, spans, and structural counts.
- `analyzer/complexity_analyzer.py`: Radon complexity and maintainability index.
- `analyzer/dependency_analyzer.py`: module resolution, graph construction, degrees, and cycles.
- `analyzer/metric_calculator.py`: module aggregation from previously calculated inputs.
- `analyzer/confusion_score.py`: explainable function, class, module, and project scoring.
- `analyzer/recommendations.py`: threshold-based advisory issues.
- `analyzer/duplication_analyzer.py`: deferred duplicate-analysis interface only.
- `services/analysis_service.py`: safe end-to-end orchestration.
- `services/export_service.py`: deterministic JSON and hotspot CSV serialization.
- `visualization/charts.py`: Plotly metric charts.
- `visualization/graph_layout.py`: deterministic NetworkX coordinates.
- `visualization/dependency_graph.py`: interactive Plotly graph construction and highlighting.
- `ui/sidebar.py`: analysis inputs and graph/filter controls.
- `ui/project_overview.py`: summary cards, distributions, and hotspot table.
- `ui/module_details.py`: selected-module inspector.
- `ui/function_details.py`: selected-function inspector and source excerpt.
- `ui/dashboard.py`: session-state composition and view routing.
- `app.py`: Streamlit configuration and dashboard entry point.
- `tests/sample_projects/`: deterministic integration fixtures.

---

### Task 1: Typed contracts and deterministic project scanning

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `models/__init__.py`
- Create: `models/function_info.py`
- Create: `models/class_info.py`
- Create: `models/module.py`
- Create: `models/issue.py`
- Create: `models/project.py`
- Create: `analyzer/__init__.py`
- Create: `analyzer/project_scanner.py`
- Create: `tests/test_project_scanner.py`

**Interfaces:**
- Consumes: `str | pathlib.Path`, optional ignored-name set, and optional glob patterns.
- Produces: the specification dataclasses and `ProjectScanner.scan(project_path: str | Path) -> list[Path]`.

- [ ] **Step 1: Write scanner tests before creating analyzer code**

```python
def test_scan_returns_only_sorted_python_files_and_applies_ignores(tmp_path):
    (tmp_path / "b.py").write_text("x = 1", encoding="utf-8")
    (tmp_path / "a.py").write_text("x = 1", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("skip", encoding="utf-8")
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "hidden.py").write_text("x = 1", encoding="utf-8")
    assert [path.name for path in ProjectScanner().scan(tmp_path)] == ["a.py", "b.py"]

def test_scan_applies_custom_patterns(tmp_path):
    (tmp_path / "keep.py").write_text("", encoding="utf-8")
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "skip.py").write_text("", encoding="utf-8")
    scanner = ProjectScanner(extra_ignore_patterns=["generated/**"])
    assert [path.name for path in scanner.scan(tmp_path)] == ["keep.py"]

def test_scan_rejects_invalid_directory(tmp_path):
    with pytest.raises(ValueError, match="Project path does not exist or is not a directory"):
        ProjectScanner().scan(tmp_path / "missing")
```

- [ ] **Step 2: Run the scanner suite and verify RED**

Run: `pytest tests/test_project_scanner.py -q`

Expected: collection fails because `analyzer.project_scanner` does not exist.

- [ ] **Step 3: Add the exact data contracts, dependency manifest, and minimal scanner**

```python
DEFAULT_IGNORED_NAMES = {
    ".git", ".github", ".idea", ".vscode", "__pycache__", "venv",
    ".venv", "env", "node_modules", "dist", "build", "coverage",
    ".pytest_cache", ".mypy_cache",
}

class ProjectScanner:
    def __init__(self, ignored_names=None, extra_ignore_patterns=None):
        self.ignored_names = DEFAULT_IGNORED_NAMES | (ignored_names or set())
        self.extra_ignore_patterns = tuple(extra_ignore_patterns or ())
        self.errors: list[str] = []

    def scan(self, project_path: str | Path) -> list[Path]:
        root = Path(project_path)
        if not root.exists() or not root.is_dir():
            raise ValueError("Project path does not exist or is not a directory.")
        # Walk with os.scandir, skip ignored names/symlink directories before descent,
        # match relative POSIX paths with PurePath.match, collect permission errors,
        # and return sorted resolved .py paths.
```

Create the five dataclass modules with every field and default shown in the source specification. Re-export all contracts from `models/__init__.py`. Use these requirement lines:

```text
networkx>=3.2,<4
plotly>=5.18,<7
radon>=6.0,<7
streamlit>=1.40,<2
pytest>=8.0,<9
```

- [ ] **Step 4: Verify scanner acceptance and regression gates**

Run: `pytest tests/test_project_scanner.py -q`

Expected: all six required scanner behaviors pass, including repeated stable ordering and a custom ignored name.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit the foundation slice**

```bash
git add .gitignore requirements.txt models analyzer tests/test_project_scanner.py
git commit -m "feat: add analysis contracts and project scanner"
```

### Task 2: AST symbol and structural analysis

**Files:**
- Create: `analyzer/ast_analyzer.py`
- Create: `tests/test_ast_analyzer.py`

**Interfaces:**
- Consumes: `FunctionMetrics`, `ClassMetrics`, a path, and an already-read source string.
- Produces: `ASTAnalyzer.analyze_file(file_path, source) -> tuple[list[FunctionMetrics], list[ClassMetrics], dict]` with `imports`, `from_imports`, and `syntax_error` metadata.

- [ ] **Step 1: Write focused extraction tests**

```python
SOURCE = '''
import os
from package import helper
class Worker:
    async def run(self, value, flag=False):
        if flag:
            for item in value:
                if item:
                    return helper(item)
        return None
def outer(arg):
    def inner():
        return arg
    return inner()
'''

def test_extracts_async_method_counts_and_qualified_name():
    functions, classes, metadata = ASTAnalyzer().analyze_file("sample.py", SOURCE)
    method = next(item for item in functions if item.qualified_name == "Worker.run")
    assert (method.parameters, method.branches, method.loops) == (3, 2, 1)
    assert method.nesting_depth == 3
    assert classes[0].method_count == 1
    assert metadata["imports"] == ["os"]
    assert metadata["from_imports"] == ["package.helper"]

def test_extracts_nested_function_and_line_span():
    functions, _, _ = ASTAnalyzer().analyze_file("sample.py", SOURCE)
    outer = next(item for item in functions if item.name == "outer")
    assert outer.nested_functions == 1
    assert outer.end_line >= outer.start_line

def test_syntax_error_is_metadata_not_exception():
    functions, classes, metadata = ASTAnalyzer().analyze_file("broken.py", "def broken(:\n")
    assert functions == [] and classes == []
    assert "SyntaxError" in metadata["syntax_error"]
```

- [ ] **Step 2: Run AST tests and verify RED**

Run: `pytest tests/test_ast_analyzer.py -q`

Expected: import failure for `analyzer.ast_analyzer`.

- [ ] **Step 3: Implement a scoped AST visitor**

```python
class ASTAnalyzer:
    def analyze_file(self, file_path: str | Path, source: str):
        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as exc:
            message = f"{file_path}:{exc.lineno or '?'}: SyntaxError: {exc.msg}"
            return [], [], {"imports": [], "from_imports": [], "syntax_error": message}
        visitor = _SymbolVisitor(str(file_path))
        visitor.visit(tree)
        return visitor.functions, visitor.classes, {
            "imports": sorted(visitor.imports),
            "from_imports": sorted(visitor.from_imports),
            "syntax_error": None,
        }
```

Implement `_SymbolVisitor` with a class/function name stack. For each function, walk only its body while excluding nested function/class bodies from ordinary counts; count parameters across positional-only, positional, keyword-only, `*args`, and `**kwargs`; calculate maximum nesting over the required AST node types; and separately count branches, loops, try blocks, returns, calls, assigned local names, and immediate nested definitions. Initialize complexity to `1`; Task 3 replaces it from Radon.

- [ ] **Step 4: Verify all eleven AST behaviors and full suite**

Run: `pytest tests/test_ast_analyzer.py -q`

Expected: PASS for normal/async/nested functions, methods, parameters, spans, branches, loops, try blocks, nesting, and syntax errors.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit AST analysis**

```bash
git add analyzer/ast_analyzer.py tests/test_ast_analyzer.py
git commit -m "feat: extract Python structure with AST"
```

### Task 3: Radon complexity and maintainability metrics

**Files:**
- Create: `analyzer/complexity_analyzer.py`
- Create: `tests/test_complexity_analyzer.py`

**Interfaces:**
- Consumes: a source string already held by `AnalysisService`.
- Produces: `ComplexityAnalyzer.function_complexities(source) -> dict[str, int]` and `maintainability_index(source) -> float | None`.

- [ ] **Step 1: Write behavior-first Radon tests**

```python
def test_branching_function_is_more_complex_than_straight_line():
    analyzer = ComplexityAnalyzer()
    simple = analyzer.function_complexities("def f():\n    return 1\n")["f"]
    branching = analyzer.function_complexities(
        "def f(x):\n    if x:\n        return 1\n    return 0\n"
    )["f"]
    assert simple < branching

def test_maintainability_index_is_numeric_for_valid_source():
    value = ComplexityAnalyzer().maintainability_index("def f():\n    return 1\n")
    assert isinstance(value, float)
    assert 0 <= value <= 100

def test_invalid_source_returns_safe_values():
    analyzer = ComplexityAnalyzer()
    assert analyzer.function_complexities("def f(:") == {}
    assert analyzer.maintainability_index("def f(:") is None
```

- [ ] **Step 2: Run complexity tests and verify RED**

Run: `pytest tests/test_complexity_analyzer.py -q`

Expected: import failure for `analyzer.complexity_analyzer`.

- [ ] **Step 3: Add minimal Radon adapter**

```python
class ComplexityAnalyzer:
    def function_complexities(self, source: str) -> dict[str, int]:
        try:
            blocks = cc_visit(source)
        except (SyntaxError, ValueError):
            return {}
        values: dict[str, int] = {}
        for block in blocks:
            if block.__class__.__name__ in {"Function", "Method"}:
                values[getattr(block, "fullname", block.name)] = int(block.complexity)
        return dict(sorted(values.items()))

    def maintainability_index(self, source: str) -> float | None:
        try:
            return round(float(mi_visit(source, multi=True)), 2)
        except (SyntaxError, ValueError, ZeroDivisionError):
            return None
```

- [ ] **Step 4: Verify complexity gate and regression suite**

Run: `pytest tests/test_complexity_analyzer.py -q`

Expected: PASS.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit complexity analysis**

```bash
git add analyzer/complexity_analyzer.py tests/test_complexity_analyzer.py
git commit -m "feat: calculate Radon code metrics"
```

### Task 4: Internal dependency graph and module resolution

**Files:**
- Create: `analyzer/dependency_analyzer.py`
- Create: `tests/test_dependency_analyzer.py`

**Interfaces:**
- Consumes: discovered module names and raw absolute/relative import strings.
- Produces: `build_graph`, `find_cycles`, `calculate_degrees`, plus `module_name_for_path` and `resolve_internal_imports` helpers used by the service.

- [ ] **Step 1: Write graph and resolution tests**

```python
def test_build_graph_excludes_external_modules_and_preserves_isolates():
    graph = DependencyAnalyzer().build_graph(
        {"a", "b", "isolated"}, {"a": ["b", "requests"], "b": []}
    )
    assert sorted(graph.nodes) == ["a", "b", "isolated"]
    assert sorted(graph.edges) == [("a", "b")]

def test_degrees_and_cycles_are_deterministic():
    analyzer = DependencyAnalyzer()
    graph = analyzer.build_graph(
        {"a", "b", "c"}, {"a": ["b", "c"], "b": ["a"], "c": []}
    )
    assert analyzer.calculate_degrees(graph)["a"] == (1, 2)
    assert analyzer.find_cycles(graph) == [["a", "b"]]

def test_relative_import_resolves_inside_package():
    modules = {"pkg", "pkg.api", "pkg.helpers"}
    resolved = resolve_internal_imports("pkg.api", [], [".helpers.run"], modules)
    assert resolved == ["pkg.helpers"]
```

- [ ] **Step 2: Run dependency tests and verify RED**

Run: `pytest tests/test_dependency_analyzer.py -q`

Expected: import failure for `analyzer.dependency_analyzer`.

- [ ] **Step 3: Implement deterministic graph behavior**

```python
class DependencyAnalyzer:
    def build_graph(self, module_names, imports_by_module):
        graph = nx.DiGraph()
        graph.add_nodes_from(sorted(module_names))
        for source in sorted(module_names):
            for target in sorted(set(imports_by_module.get(source, []))):
                if target in module_names and target != source:
                    graph.add_edge(source, target)
        return graph

    def find_cycles(self, graph):
        groups = [sorted(group) for group in nx.strongly_connected_components(graph) if len(group) > 1]
        return sorted(groups)

    def calculate_degrees(self, graph):
        return {name: (graph.in_degree(name), graph.out_degree(name)) for name in sorted(graph.nodes)}
```

`module_name_for_path(root, path)` removes `.py`, turns separators into dots, and collapses a terminal `.__init__`. `resolve_internal_imports()` resolves the longest discovered internal module prefix, handles leading dots relative to the importing package, and returns sorted unique modules; standard-library and third-party imports remain external.

- [ ] **Step 4: Verify dependency gate and full suite**

Run: `pytest tests/test_dependency_analyzer.py -q`

Expected: PASS for internal/external edges, isolates, degrees, cycles, package modules, and relative imports.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit dependency analysis**

```bash
git add analyzer/dependency_analyzer.py tests/test_dependency_analyzer.py
git commit -m "feat: map internal Python dependencies"
```

### Task 5: Module aggregation and explainable confusion scoring

**Files:**
- Create: `analyzer/metric_calculator.py`
- Create: `analyzer/confusion_score.py`
- Create: `tests/test_confusion_score.py`
- Create: `tests/test_metric_calculator.py`

**Interfaces:**
- Consumes: completed function/class metrics and dependency/maintainability values.
- Produces: `MetricCalculator.calculate_module_metrics(...) -> ModuleMetrics` and all four required `ConfusionScorer` methods.

- [ ] **Step 1: Write score relationship and aggregation tests**

```python
def function_metric(**changes):
    values = dict(name="f", qualified_name="f", file_path="x.py", start_line=1,
                  end_line=10, lines=10, parameters=1, complexity=2,
                  nesting_depth=1, branches=1, loops=0, try_blocks=0,
                  returns=1, calls=1, local_variables=1, nested_functions=0)
    values.update(changes)
    return FunctionMetrics(**values)

def test_high_risk_function_scores_higher_and_contributions_reconcile():
    scorer = ConfusionScorer()
    low_score, _ = scorer.score_function(function_metric())
    high_score, contributions = scorer.score_function(function_metric(
        end_line=130, lines=130, complexity=25, nesting_depth=7,
        parameters=10, branches=20, local_variables=30, calls=35,
        nested_functions=4,
    ))
    assert 0 <= low_score < high_score <= 100
    assert sum(item.points for item in contributions) == pytest.approx(high_score, abs=0.05)

def test_project_hotspot_proportion_increases_score():
    scorer = ConfusionScorer()
    calm = [module_metric(name=f"m{i}", confusion_score=20) for i in range(4)]
    hot = [module_metric(name=f"m{i}", confusion_score=90) for i in range(4)]
    assert scorer.score_project(calm, []) < scorer.score_project(hot, [])
```

Add `MetricCalculator` coverage asserting LOC, counts, average/max complexity, largest function score, sorted import lists, and every passed graph/MI field.

- [ ] **Step 2: Run score and metric tests and verify RED**

Run: `pytest tests/test_confusion_score.py tests/test_metric_calculator.py -q`

Expected: import failures for the two missing analyzer modules.

- [ ] **Step 3: Implement normalization, contributions, and module aggregation**

```python
def capped_ratio(value: float, concern_start: float, high_risk: float) -> float:
    if value <= concern_start:
        return 0.0
    if value >= high_risk:
        return 100.0
    return (value - concern_start) / (high_risk - concern_start) * 100.0

FUNCTION_RULES = (
    ("Cyclomatic Complexity", "complexity", 5, 25, 0.25),
    ("Function Length", "lines", 20, 120, 0.20),
    ("Nesting Depth", "nesting_depth", 2, 7, 0.20),
    ("Parameter Count", "parameters", 4, 10, 0.10),
    ("Branches", "branches", 4, 20, 0.10),
    ("Local Variables", "local_variables", 8, 30, 0.05),
    ("Function Calls", "calls", 8, 35, 0.05),
    ("Nested Functions", "nested_functions", 0, 4, 0.05),
)
```

For each rule, create a contribution with `points = normalized * weight`; round contributions to four decimals and final scores to two decimals. Implement module weights exactly as specified, using capped ratios for average complexity, maximum function score, LOC, fan-out, fan-in, cycles, inverse maintainability index, and average/max class complexity. Score classes from method complexity and class length. Score projects as `0.70 * capped-LOC-weighted-average + 0.20 * hotspot-proportion-risk + 0.10 * cycle-risk`.

`MetricCalculator` counts nonblank source lines, computes aggregates with zero-safe defaults, and never scans or parses source.

- [ ] **Step 4: Verify score acceptance and regression gates**

Run: `pytest tests/test_confusion_score.py tests/test_metric_calculator.py -q`

Expected: PASS for bounds, monotonic relationships, contribution reconciliation, module aggregation, and hotspot/cycle project penalties.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit explainable scoring**

```bash
git add analyzer/metric_calculator.py analyzer/confusion_score.py tests/test_confusion_score.py tests/test_metric_calculator.py
git commit -m "feat: calculate explainable confusion scores"
```

### Task 6: Advisory recommendation engine

**Files:**
- Create: `analyzer/recommendations.py`
- Create: `tests/test_recommendations.py`

**Interfaces:**
- Consumes: scored `FunctionMetrics`, `ModuleMetrics`, and cycle groups.
- Produces: the three required `RecommendationEngine` methods returning sorted `CodeIssue` lists.

- [ ] **Step 1: Write threshold and wording tests**

```python
@pytest.mark.parametrize(
    ("changes", "issue_type"),
    [
        ({"lines": 61}, "large_function"),
        ({"nesting_depth": 5}, "deep_nesting"),
        ({"complexity": 16}, "high_complexity"),
        ({"parameters": 8}, "too_many_parameters"),
    ],
)
def test_function_rule_triggers(changes, issue_type):
    issues = RecommendationEngine().for_function(function_metric(**changes))
    assert issue_type in {issue.issue_type for issue in issues}
    assert all("bad" not in issue.message.lower() for issue in issues)

def test_module_fan_out_and_cycle_rules_are_advisory():
    engine = RecommendationEngine(fan_out_threshold=5)
    assert engine.for_module(module_metric(fan_out=6))[0].issue_type == "high_fan_out"
    cycle = engine.for_cycles([["a", "b"]])[0]
    assert cycle.issue_type == "circular_dependency"
    assert cycle.severity in {"medium", "high"}
```

- [ ] **Step 2: Run recommendation tests and verify RED**

Run: `pytest tests/test_recommendations.py -q`

Expected: import failure for `analyzer.recommendations`.

- [ ] **Step 3: Implement exact recommendation rules**

```python
class RecommendationEngine:
    def __init__(self, fan_out_threshold: int = 8) -> None:
        self.fan_out_threshold = fan_out_threshold

    def for_function(self, metrics: FunctionMetrics) -> list[CodeIssue]:
        issues = []
        if metrics.lines > 60:
            issues.append(_issue("large_function", "medium",
                "Consider splitting this function into smaller units representing separate responsibilities.",
                metrics, metrics.lines, 60))
        # Apply nesting >= 5, complexity > 15, and parameters > 7 with the
        # exact advisory messages and relevant metric/threshold values.
        return issues
```

Module fan-out triggers above the configured threshold. Cycle issues use the joined cycle as `symbol_name` and the specified shared-responsibility message. Sort by severity rank, file path, symbol, and issue type.

- [ ] **Step 4: Verify recommendation gate and full suite**

Run: `pytest tests/test_recommendations.py -q`

Expected: PASS for all six rules and non-insulting language.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit recommendations**

```bash
git add analyzer/recommendations.py tests/test_recommendations.py
git commit -m "feat: generate maintainability recommendations"
```

### Task 7: End-to-end analysis service and fixture projects

**Files:**
- Create: `services/__init__.py`
- Create: `services/analysis_service.py`
- Create: `analyzer/duplication_analyzer.py`
- Create: `tests/test_analysis_service.py`
- Create: `tests/sample_projects/simple_project/app.py`
- Create: `tests/sample_projects/simple_project/helpers.py`
- Create: `tests/sample_projects/complex_project/processor.py`
- Create: `tests/sample_projects/circular_import_project/a.py`
- Create: `tests/sample_projects/circular_import_project/b.py`
- Create: `tests/sample_projects/deep_nesting_project/nested.py`
- Create: `tests/sample_projects/syntax_error_project/broken.py`
- Create: `tests/sample_projects/syntax_error_project/valid.py`
- Create: `tests/sample_projects/ignored_folders_project/visible.py`
- Create: `tests/sample_projects/ignored_folders_project/.venv/hidden.py`

**Interfaces:**
- Consumes: all completed analyzer interfaces and fixture project paths.
- Produces: `AnalysisService.analyze_project(project_path, extra_ignore_patterns=None) -> ProjectAnalysis`; reserves `DuplicateMatch` and `DuplicationAnalyzer.compare_functions(...)` without invoking duplicate analysis.

- [ ] **Step 1: Create fixture sources and write integration tests**

```python
def test_analyze_simple_project_returns_complete_metrics():
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    assert analysis.python_file_count == 2
    assert analysis.function_count >= 2
    assert {module.name for module in analysis.modules} == {"app", "helpers"}
    assert ("app", "helpers") in analysis.dependency_edges
    assert all(0 <= function.confusion_score <= 100 for function in analysis.functions)
    assert all(function.score_contributions for function in analysis.functions)

def test_analyze_cycle_and_syntax_error_projects_without_global_failure():
    circular = AnalysisService().analyze_project(SAMPLES / "circular_import_project")
    assert circular.circular_dependencies == [["a", "b"]]
    partial = AnalysisService().analyze_project(SAMPLES / "syntax_error_project")
    assert partial.python_file_count == 2
    assert partial.function_count == 1
    assert any("SyntaxError" in error and "broken.py" in error for error in partial.errors)
```

The simple fixture has `app.py` importing `helpers`, one branch, and `helpers.py` containing a class method. The circular fixture files import each other. The syntax fixture has one invalid definition and one valid function. The ignored fixture places valid code under `.venv` to prove exclusion.

- [ ] **Step 2: Run service tests and verify RED**

Run: `pytest tests/test_analysis_service.py -q`

Expected: import failure for `services.analysis_service`.

- [ ] **Step 3: Implement the orchestration pipeline in required order**

```python
class AnalysisService:
    def analyze_project(self, project_path: str | Path, extra_ignore_patterns=None) -> ProjectAnalysis:
        root = Path(project_path)
        scanner = ProjectScanner(extra_ignore_patterns=extra_ignore_patterns)
        paths = scanner.scan(root)
        sources, errors = self._read_sources(paths)
        # Analyze each readable source once, apply Radon values to matching AST
        # functions, resolve modules/imports, build graph/degrees/cycles, aggregate
        # and score metrics, then generate issues and the final sorted result.
```

`_read_sources()` attempts UTF-8 once and records `path: ExceptionType: message` for failures. Syntax metadata errors join this list. Map Radon results by exact qualified name, then by terminal name when unique. Assign cycle counts to every participating module. Apply class/function scores before module aggregation, then module and project scores. Count all discovered Python files even if a file is unreadable or syntactically invalid.

`duplication_analyzer.py` defines the required dataclass and method signature; the method raises `NotImplementedError("Duplicate detection is deferred from the MVP.")`. `AnalysisService` never constructs it.

- [ ] **Step 4: Verify service acceptance and all earlier phase gates**

Run: `pytest tests/test_analysis_service.py -q`

Expected: PASS for counts, errors, functions, modules, edges, cycles, contributions, issues, and project score.

Run: `pytest tests/test_project_scanner.py tests/test_ast_analyzer.py tests/test_complexity_analyzer.py tests/test_dependency_analyzer.py tests/test_confusion_score.py tests/test_recommendations.py tests/test_analysis_service.py -q`

Expected: PASS.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit the complete analysis core**

```bash
git add services analyzer/duplication_analyzer.py tests/test_analysis_service.py tests/sample_projects
git commit -m "feat: orchestrate complete project analysis"
```

### Task 8: Deterministic JSON and hotspot CSV export

**Files:**
- Create: `services/export_service.py`
- Create: `tests/test_export_service.py`

**Interfaces:**
- Consumes: completed `ProjectAnalysis` only.
- Produces: `ExportService.to_json(analysis) -> str` and `hotspot_csv(analysis) -> str`.

- [ ] **Step 1: Write serialization tests using a real analyzed fixture**

```python
def test_json_contains_only_serializable_analysis_data():
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    payload = json.loads(ExportService().to_json(analysis))
    assert payload["project_name"] == "simple_project"
    assert isinstance(payload["dependency_edges"], list)
    assert isinstance(payload["modules"][0]["score_contributions"], list)

def test_hotspot_csv_contains_function_and_module_rows():
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    rows = list(csv.DictReader(io.StringIO(ExportService().hotspot_csv(analysis))))
    assert {row["Type"] for row in rows} == {"Function", "Module"}
    assert list(rows[0]) == ["Name", "Type", "File", "Confusion Score", "Complexity", "Lines", "Nesting", "Issues"]
```

- [ ] **Step 2: Run export tests and verify RED**

Run: `pytest tests/test_export_service.py -q`

Expected: import failure for `services.export_service`.

- [ ] **Step 3: Implement recursive dataclass JSON and aligned CSV rows**

```python
class ExportService:
    def to_json(self, analysis: ProjectAnalysis) -> str:
        return json.dumps(asdict(analysis), indent=2, sort_keys=True, ensure_ascii=False)

    def hotspot_csv(self, analysis: ProjectAnalysis) -> str:
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=HOTSPOT_COLUMNS)
        writer.writeheader()
        # Emit sorted module rows followed by sorted function rows, with issue
        # counts matched by file/symbol and numeric values formatted to 2 decimals.
        return buffer.getvalue()
```

- [ ] **Step 4: Verify export and full regression suites**

Run: `pytest tests/test_export_service.py -q`

Expected: PASS.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit export support**

```bash
git add services/export_service.py tests/test_export_service.py
git commit -m "feat: export analysis as JSON and CSV"
```

### Task 9: Pure chart and dependency-graph visualization layer

**Files:**
- Create: `visualization/__init__.py`
- Create: `visualization/charts.py`
- Create: `visualization/graph_layout.py`
- Create: `visualization/dependency_graph.py`
- Create: `tests/test_visualizations.py`

**Interfaces:**
- Consumes: `ProjectAnalysis`, a selected module name, and graph display settings.
- Produces: Plotly `Figure` objects without importing Streamlit or recalculating analysis.

- [ ] **Step 1: Write figure-contract and empty-data tests**

```python
def test_required_charts_render_from_analysis():
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    figures = [
        complexity_distribution(analysis), confusion_distribution(analysis),
        size_vs_complexity(analysis), dependency_risk(analysis),
    ]
    assert all(isinstance(figure, go.Figure) for figure in figures)
    assert all(figure.data for figure in figures)

def test_dependency_graph_preserves_nodes_and_customdata():
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    figure = dependency_figure(analysis, selected_module="app")
    node_trace = figure.data[-1]
    assert set(node_trace.customdata) == {"app", "helpers"}
    assert "module" in node_trace.hovertemplate.lower()

def test_empty_analysis_returns_annotated_figures(empty_analysis):
    assert confusion_distribution(empty_analysis).layout.annotations[0].text == "No data available"
```

- [ ] **Step 2: Run visualization tests and verify RED**

Run: `pytest tests/test_visualizations.py -q`

Expected: import failures for `visualization.charts` and `visualization.dependency_graph`.

- [ ] **Step 3: Build deterministic Plotly figures**

```python
def graph_positions(graph: nx.DiGraph) -> dict[str, tuple[float, float]]:
    if not graph.nodes:
        return {}
    return {name: tuple(value) for name, value in nx.spring_layout(graph, seed=42).items()}

def dependency_figure(analysis, selected_module=None, size_by="score"):
    graph = nx.DiGraph()
    graph.add_nodes_from(module.name for module in analysis.modules)
    graph.add_edges_from(analysis.dependency_edges)
    positions = graph_positions(graph)
    # Create one muted edge trace, highlighted dependency/dependent edge traces,
    # and a node trace with module-name customdata for Streamlit selection.
```

Use fixed bucket labels from the specification. The scatter uses module LOC, average complexity, and score bubble size. Dependency risk plots fan-in versus fan-out. Every empty helper returns an annotated figure. Use stable module ordering and a fixed layout seed.

- [ ] **Step 4: Verify visualization boundary and regression suite**

Run: `pytest tests/test_visualizations.py -q`

Expected: PASS.

Run: `rg -n "streamlit|st\." visualization analyzer services models`

Expected: no Streamlit imports outside `ui/` and `app.py` (the command should return no matches at this point).

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit visualization primitives**

```bash
git add visualization tests/test_visualizations.py
git commit -m "feat: visualize metrics and dependencies"
```

### Task 10: Streamlit controls, overview, and hotspot navigation

**Files:**
- Create: `ui/__init__.py`
- Create: `ui/sidebar.py`
- Create: `ui/project_overview.py`
- Create: `ui/dashboard.py`
- Create: `app.py`
- Create: `tests/test_ui_helpers.py`

**Interfaces:**
- Consumes: `AnalysisService`, `ExportService`, completed analysis, and Streamlit session state.
- Produces: `render_dashboard()`, `render_sidebar()`, `render_overview()`, and pure `hotspot_rows()`/`summary_values()` helpers.

- [ ] **Step 1: Write pure overview-model tests before UI code**

```python
def test_hotspot_rows_have_required_columns_and_descending_scores():
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    rows = hotspot_rows(analysis)
    assert list(rows[0]) == ["Name", "Type", "File", "Confusion Score", "Complexity", "Lines", "Nesting", "Issues"]
    assert [row["Confusion Score"] for row in rows] == sorted(
        [row["Confusion Score"] for row in rows], reverse=True
    )

def test_summary_values_include_all_six_cards():
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    assert list(summary_values(analysis)) == [
        "Overall Confusion", "Python Files", "Functions", "Classes",
        "Circular Dependencies", "High-risk Functions",
    ]
```

- [ ] **Step 2: Run UI-helper tests and verify RED**

Run: `pytest tests/test_ui_helpers.py -q`

Expected: import failure for `ui.project_overview`.

- [ ] **Step 3: Implement session state, sidebar, overview, and dashboard shell**

```python
SESSION_DEFAULTS = {
    "project_path": "", "analysis": None, "selected_module": None,
    "selected_function": None, "risk_filter": "All", "graph_size_by": "Score",
    "ignore_patterns": "",
}

def initialize_session_state() -> None:
    for key, value in SESSION_DEFAULTS.items():
        st.session_state.setdefault(key, value)

def main() -> None:
    st.set_page_config(page_title="PyAtlas", page_icon="🗺️", layout="wide")
    initialize_session_state()
    render_dashboard()
```

`render_sidebar()` returns an analyze request containing the stripped project path and nonempty newline-separated ignore patterns. `render_dashboard()` replaces `analysis` only after a successful service call, catches the fatal validation error for display, shows partial errors as warnings, renders the heuristic disclaimer, overview cards, chart row, sortable `st.dataframe`, and JSON/CSV download buttons. Row selection stores the matching function or module identifier.

- [ ] **Step 4: Verify overview helpers, app import, and regressions**

Run: `pytest tests/test_ui_helpers.py -q`

Expected: PASS.

Run: `python -c "import app; assert callable(app.main)"`

Expected: exits 0 without starting a server.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit the usable dashboard overview**

```bash
git add app.py ui tests/test_ui_helpers.py
git commit -m "feat: add Streamlit analysis dashboard"
```

### Task 11: Module and function inspectors with graph selection

**Files:**
- Create: `ui/module_details.py`
- Create: `ui/function_details.py`
- Modify: `ui/dashboard.py`
- Modify: `ui/project_overview.py`
- Create: `tests/test_detail_helpers.py`

**Interfaces:**
- Consumes: selected module/function identifiers and completed analysis.
- Produces: `render_module_details`, `render_function_details`, safe `source_excerpt`, and dependency-graph selection routing.

- [ ] **Step 1: Write detail lookup and safe source-preview tests**

```python
def test_source_excerpt_returns_requested_numbered_lines(tmp_path):
    path = tmp_path / "sample.py"
    path.write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")
    assert source_excerpt(str(path), 2, 3) == "2: two\n3: three"

def test_source_excerpt_reports_missing_file_without_raising(tmp_path):
    text = source_excerpt(str(tmp_path / "missing.py"), 1, 2)
    assert text.startswith("Source preview unavailable:")

def test_module_relations_are_sorted():
    analysis = AnalysisService().analyze_project(SAMPLES / "simple_project")
    dependencies, dependents = module_relations(analysis, "helpers")
    assert dependencies == []
    assert dependents == ["app"]
```

- [ ] **Step 2: Run detail-helper tests and verify RED**

Run: `pytest tests/test_detail_helpers.py -q`

Expected: import failures for the detail modules.

- [ ] **Step 3: Implement inspectors and graph-to-state routing**

```python
def source_excerpt(file_path: str, start_line: int, end_line: int) -> str:
    try:
        lines = Path(file_path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return f"Source preview unavailable: {type(exc).__name__}: {exc}"
    start = max(start_line, 1)
    stop = min(end_line, len(lines))
    return "\n".join(f"{number}: {lines[number - 1]}" for number in range(start, stop + 1))
```

Module details show every required metric, sorted dependencies/dependents, matching issues, and contribution bars. Function details show all required metrics, contribution bars, matching recommendations, and a bounded source excerpt. `dashboard.py` renders the graph with `on_select="rerun"`; a selected node's `customdata` updates `selected_module`. Hotspot selections update the corresponding inspector and clear the other symbol selection.

- [ ] **Step 4: Verify detail flows and full suite**

Run: `pytest tests/test_detail_helpers.py tests/test_ui_helpers.py tests/test_visualizations.py -q`

Expected: PASS.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit complete exploration views**

```bash
git add ui tests/test_detail_helpers.py
git commit -m "feat: inspect modules and functions"
```

### Task 12: Documentation and production-readiness verification

**Files:**
- Modify: `README.md`
- Modify: `.gitignore`
- Create: `tests/test_app_smoke.py`

**Interfaces:**
- Consumes: the complete application entry point and public user workflow.
- Produces: documented setup/operation and an automated Streamlit application smoke test.

- [ ] **Step 1: Write a Streamlit AppTest smoke test**

```python
from streamlit.testing.v1 import AppTest

def test_app_renders_initial_state_without_exception():
    app = AppTest.from_file("app.py")
    app.run(timeout=15)
    assert not app.exception
    assert any("PyAtlas" in item.value for item in app.title)
    assert app.button(key="analyze_project")
```

- [ ] **Step 2: Run smoke test and verify RED for the missing stable widget contract**

Run: `pytest tests/test_app_smoke.py -q`

Expected: FAIL until the dashboard title and Analyze button key exactly match the asserted public UI contract.

- [ ] **Step 3: Stabilize widget keys and replace the README with complete operating documentation**

The README must contain these concrete sections: Overview, Problem, Screenshot placeholder, Features, Architecture, Installation, Running PyAtlas, Running Tests, Confusion Score, Limitations, Supported Python Versions, and Roadmap. Include these commands verbatim:

```bash
python -m venv .venv
pip install -r requirements.txt
streamlit run app.py
pytest -q
```

Document that scores are heuristic, large files are not automatically bad, only local Python projects are supported, syntax errors are isolated, Python 3.12+ is required, and duplicate detection/history/CLI/CI analysis remain future work. Add `.streamlit/` local secrets and common Python build artifacts to `.gitignore` without ignoring source fixtures.

- [ ] **Step 4: Run final automated verification**

Run: `pytest -q`

Expected: every test passes with no warnings emitted by project code.

Run: `python -m compileall -q app.py analyzer models services ui visualization`

Expected: exits 0.

Run: `python -m streamlit run app.py --server.headless true --server.port 8765`

Expected: server reports a local URL and remains healthy until manually stopped after the startup check.

Run: `git diff --check`

Expected: no whitespace errors.

- [ ] **Step 5: Confirm source-architecture boundaries**

Run: `rg -n "import streamlit|from streamlit" analyzer models services visualization`

Expected: no matches.

Run: `rg -n "ast\.|radon|networkx" app.py ui`

Expected: no analysis-library use in UI code.

- [ ] **Step 6: Commit the production-ready MVP**

```bash
git add README.md .gitignore tests/test_app_smoke.py app.py ui
git commit -m "docs: complete PyAtlas MVP guide and verification"
```

## Final acceptance checklist

- [ ] A valid local Python project produces a complete `ProjectAnalysis`.
- [ ] Default/custom ignores and invalid-root validation behave exactly as specified.
- [ ] Syntax, permission, encoding, and analyzer failures remain file-local.
- [ ] Function/class spans and structural counts are correct for sync, async, nested, and method symbols.
- [ ] Radon complexity and maintainability index values are mapped to the correct symbols/modules.
- [ ] Only internal modules appear in the dependency graph; isolated nodes and cycles are preserved.
- [ ] Function, class, module, and project scores remain within 0–100 and retain reconciling contributions.
- [ ] Recommendations use the required advisory language and thresholds.
- [ ] Dashboard state persists across reruns and all required cards, tables, charts, graph interactions, and inspectors render.
- [ ] JSON contains no custom objects and CSV rows align with the hotspot table.
- [ ] Duplicate detection is clearly deferred behind its reserved interface.
- [ ] `pytest -q`, compilation, architecture scans, and headless Streamlit startup all pass.
