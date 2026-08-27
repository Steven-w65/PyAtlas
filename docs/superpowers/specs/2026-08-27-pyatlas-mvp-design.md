# PyAtlas MVP Design

**Date:** 2026-08-27

**Status:** Approved

**Source requirements:** `pyatlas-codex-spec.md`, supplied with the implementation request.

## Product outcome

PyAtlas is a local, production-quality Python 3.12+ application that analyzes a Python project and presents an interactive, explainable map of maintainability risk. A user can point the application at a local project, identify structural hotspots, inspect the metrics that produced each score, explore internal dependencies and cycles, and export the results.

The first workable version includes the complete MVP through export. Duplicate-code detection remains intentionally deferred because the source requirements place it after the initial MVP; the dedicated analyzer module and public interface remain reserved so it can be added without restructuring the application.

The central product rule is that every risk score must explain where the risk is concentrated, why it scored highly, and what the developer should inspect first. Scores are heuristic signals, not objective judgments about code quality.

## Scope

The MVP includes:

- deterministic discovery of local Python files with default and custom ignores;
- AST extraction of functions, async functions, methods, classes, imports, source spans, and structural metrics;
- Radon cyclomatic complexity and maintainability index calculations;
- internal dependency mapping, fan-in, fan-out, isolated modules, and circular dependency detection;
- function, class, module, and project confusion scores with contribution records;
- advisory recommendations derived from explicit thresholds;
- a Streamlit dashboard with summary metrics, hotspots, charts, an interactive dependency graph, and module/function inspectors;
- JSON and hotspot CSV exports;
- automated analyzer, service, export, visualization-helper, and startup tests;
- installation, operation, architecture, limitations, and roadmap documentation.

The MVP excludes authentication, cloud services, repository hosting integration, source rewriting, artificial intelligence, history or pull-request analysis, background processing, plugin systems, multiple languages, and the optional duplicate comparison algorithm.

## Architecture

The implementation uses five strict layers with dependencies flowing toward typed data contracts:

1. `models/` contains dataclasses for `ScoreContribution`, `FunctionMetrics`, `ClassMetrics`, `ModuleMetrics`, `CodeIssue`, and `ProjectAnalysis`. Core components exchange these models rather than unstructured dictionaries.
2. `analyzer/` contains deterministic, Streamlit-free analysis logic. Each analyzer has one responsibility and exposes the public interfaces from the source requirements.
3. `services/` coordinates analysis and serialization. `AnalysisService` is the single analysis entry point used by the interface, while `ExportService` converts completed models to JSON and CSV.
4. `visualization/` converts already-calculated models into Plotly figures and dependency graph data. It performs no source analysis.
5. `ui/` composes Streamlit controls and views. `app.py` configures Streamlit, initializes session state, and invokes the dashboard; it contains no analysis rules.

This boundary keeps the analyzer and service layers independently runnable under pytest and allows a future CLI or CI integration to reuse the same application core.

## Vertical delivery slices

The program will be implemented in runnable vertical slices while retaining every phase-specific acceptance gate from the source requirements:

1. Typed models, project scanning, safe source discovery, and scanner tests.
2. AST extraction and Radon complexity with symbol mapping and tests.
3. Internal dependency resolution, cycle analysis, and module aggregation with tests.
4. Explainable scoring and advisory recommendations with tests.
5. End-to-end analysis orchestration and exports with fixture-project integration tests.
6. Streamlit overview, summary cards, filters, and hotspot exploration.
7. Charts, interactive dependency graph, and module/function detail views.
8. Documentation, full regression verification, Python compilation, and a headless Streamlit startup smoke check.

Later slices do not begin until the targeted gate for their prerequisites passes. The full test suite runs at each slice boundary.

## Data contracts

The public dataclasses and method signatures follow the supplied specification without incompatible changes. Lists use deterministic ordering. File paths stored in analysis results are normalized strings; display surfaces prefer project-relative paths where context is clear. `ProjectAnalysis.errors` stores user-readable error records for file-level failures.

Analysis results are treated as immutable after construction even though standard dataclasses remain mutable. Scoring is applied before the final `ProjectAnalysis` object is exposed to UI or export consumers. Contribution point totals reconcile with their owning score subject only to normal floating-point rounding.

The reserved `DuplicationAnalyzer.compare_functions()` interface and `DuplicateMatch` dataclass will be present, but duplicate analysis will not be invoked by `AnalysisService` in the MVP.

## Analysis data flow

`AnalysisService.analyze_project()` performs the following pipeline:

1. Validate that the supplied path exists and is a directory.
2. Scan deterministic Python file paths using default ignored names plus user patterns.
3. Read each source file once as UTF-8 and retain source text for the analysis run.
4. Analyze readable sources with `ASTAnalyzer` to produce structural metrics and import metadata.
5. Calculate per-symbol complexity and per-module maintainability index with Radon.
6. Derive stable project-relative module names, including packages and `__init__.py` modules.
7. Resolve absolute and relative imports only against discovered project modules.
8. Build a NetworkX directed graph that includes isolated modules.
9. Calculate fan-in, fan-out, strongly connected cycles, and per-module cycle counts.
10. Aggregate functions, classes, imports, dependencies, and maintainability values into module metrics.
11. Score functions, classes, modules, and the project, storing every contribution.
12. Generate function, module, and cycle recommendations.
13. Return a complete, deterministically ordered `ProjectAnalysis`.

Radon results are mapped back to AST functions by qualified name and source-line information, with conservative fallback matching for nested symbols. External imports never become graph nodes. Relative imports are resolved from the importing module's package context.

The first version does not use a persistent cache. Reading each source once and retaining parsed results within the service run prevents avoidable repeated filesystem work and leaves a clean boundary for a future path, modification-time, and content-hash cache.

## Confusion scoring and explainability

Function scoring uses the required weights and normalization thresholds for complexity, length, nesting, parameters, branches, local variables, calls, and nested functions. Every metric produces a `ScoreContribution` containing the raw value, normalized value, weight, points, and a plain-language reason.

Module scoring uses average function complexity, largest function risk, module length, fan-out, fan-in, circular dependencies, maintainability risk, and class complexity. Size influence is capped so a large cohesive module is not automatically treated as poor code.

Project scoring combines a LOC-capped weighted module average at 70%, a hotspot-proportion penalty at 20%, and a cycle penalty at 10%. Every score is clamped to the inclusive range 0–100. Labels and UI text explicitly describe the score as a heuristic estimate.

Recommendations trigger only from explicit, testable conditions. Messages remain educational and probabilistic. No recommendation labels code as bad or automatically modifies analyzed source.

## Error handling and reliability

An invalid analysis root is the only project-wide fatal validation error and uses the required message: `Project path does not exist or is not a directory.`

File-level permission, encoding, syntax, AST, and Radon failures are isolated. The affected file is skipped or partially analyzed as appropriate, and the error record includes its path, exception type, message, and syntax line when available. Other files continue through the pipeline.

The scanner applies ignore rules before descent, does not follow directory symlinks, tolerates inaccessible entries, and returns stable path ordering. Empty projects, projects whose files all fail, isolated modules, empty charts, and missing optional metrics produce useful empty states rather than unhandled exceptions.

Core analysis is deterministic and avoids quadratic work. Duplicate detection is the sole designed exception and is deferred. No core feature requires network access.

## Streamlit experience

The application uses Streamlit's wide layout with a persistent sidebar and one exploration workspace.

The sidebar contains the project path, newline-separated ignore patterns, risk filters, graph sizing and color options, and the Analyze action. `st.session_state` retains the current path, completed analysis, selected module, selected function, filters, graph settings, and ignore patterns across reruns. Starting a new analysis is the only action that replaces the current completed result.

The main workspace contains:

1. A compact project header and the required heuristic disclaimer.
2. Six summary cards: project score, Python files, functions, classes, circular dependencies, and high-risk functions.
3. Confusion-score and complexity distributions.
4. A sortable hotspot table with the required columns and selection behavior.
5. A Plotly dependency graph with zoom, pan, hover details, click selection, and visual distinction for a selected module, its dependencies, and its dependents.
6. File-size-versus-complexity and fan-in/fan-out risk charts.
7. Module and function inspectors containing metrics, score contributions, recommendations, dependency context, and source previews.
8. JSON and CSV download actions backed by `ExportService`.

The UI stays close to native Streamlit components with restrained theme-neutral CSS. Analysis logic never enters UI modules. UI components receive a completed `ProjectAnalysis` plus explicit selection and filter values.

## Dependency graph behavior

Each discovered internal module is a graph node, including modules with no internal edges. Directed edges represent resolved internal imports. Node color represents the confusion category; node size represents the selected graph setting, defaulting to confusion score with a minimum readable size.

Hover text shows module name, score, lines, functions, classes, fan-in, and fan-out. Selecting a node updates the module inspector. The selected node, upstream dependents, and downstream dependencies use distinct visual styles while unrelated nodes remain subdued. Plotly supplies zoom, pan, reset, and hover interactions without introducing another visualization dependency.

## Export behavior

`ExportService.to_json()` recursively converts dataclasses, tuples, and nested collections into ordinary JSON-compatible values and produces deterministic formatted JSON. `hotspot_csv()` emits function and module hotspot rows aligned with the table's key metrics. Neither exporter reads source files or recalculates analysis.

## Testing strategy

Core behavior follows red-green-refactor. Each new analyzer or service behavior begins with a focused test that is observed failing for the expected missing behavior before minimal production code is added. Tests assert real results from source strings and fixture projects rather than mocked analyzer calls.

The required fixture projects cover simple code, structurally complex code, circular imports, deep nesting, syntax errors, and ignored folders. Targeted suites cover:

- scanner discovery, filtering, ordering, and validation;
- sync, async, nested, and class-method AST extraction plus structural counts and syntax errors;
- Radon complexity, maintainability index, and malformed-source containment;
- internal dependency edges, external exclusion, isolated nodes, degrees, and cycles;
- bounded score behavior, monotonic risk relationships, and contribution reconciliation;
- every recommendation threshold and advisory wording;
- complete analysis counts, metrics, dependencies, cycles, errors, and project score;
- JSON and CSV serialization;
- pure chart/graph preparation helpers and empty datasets where practical;
- application import and headless Streamlit startup.

Every vertical slice runs its targeted suite and then `pytest -q`. Final verification also compiles every Python module and starts Streamlit headlessly long enough to detect import or initialization failures. UI pixel snapshots are excluded because they are brittle and optional in the source requirements.

## Documentation and operation

The README will explain the product problem, features, architecture, Python 3.12+ setup, installation from `requirements.txt`, `streamlit run app.py`, `pytest -q`, the Confusion Score formula and limitations, screenshots or explicit placeholders, and the future roadmap. The application operates entirely on local files and requires no credentials or external services.

## Completion criteria

The MVP is complete when a valid local Python project can be analyzed without analysis logic in Streamlit; ignored folders and malformed files behave correctly; structural, complexity, dependency, cycle, maintainability, and score results are present; contribution explanations and advisory recommendations are visible; all dashboard, hotspot, graph, detail, and export flows operate; all tests pass; Python compilation succeeds; and Streamlit starts headlessly without initialization errors.

