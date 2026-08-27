# PyAtlas

PyAtlas is a local, interactive Python codebase analyzer that maps complexity, dependencies, circular imports, structural hotspots, and maintainability risk. It combines static analysis with an explainable **Confusion Score** so developers can see not only where risk is concentrated, but also which metrics produced each result.

## Problem

Traditional metric reports often provide isolated numbers without showing how they relate across a project. PyAtlas turns those signals into one navigable dashboard that helps answer:

- Which modules and functions deserve review first?
- Why did a symbol receive a high score?
- Where are dependencies concentrated?
- Which imports form circular groups?
- Which functions have deep nesting or high cyclomatic complexity?

PyAtlas is an inspection tool. It never changes analyzed source files and does not require an internet connection after installation.

## Screenshot

> Dashboard screenshot placeholder: run the application, analyze a project, and capture the overview, dependency map, and detail inspector here.

## Features

- Recursive `.py` discovery with safe default ignores and custom glob patterns
- AST extraction for synchronous, asynchronous, nested, and class methods
- Function spans, parameters, branches, loops, nesting, calls, returns, try blocks, and local-variable counts
- Radon cyclomatic complexity and maintainability index
- Internal dependency graph with fan-in, fan-out, isolated modules, and circular dependency groups
- Explainable function, class, module, and project Confusion Scores
- Metric-by-metric contribution tables for every score
- Advisory recommendations for large, deeply nested, highly complex, or highly connected code
- Sortable and filterable hotspot table
- Complexity, score-distribution, file-size, and dependency-risk charts
- Interactive dependency map with module selection and relationship highlighting
- Module and function detail inspectors with source previews
- JSON analysis export and hotspot CSV export
- Partial results when an individual file has a syntax, encoding, or permission error

## Architecture

PyAtlas separates analysis from presentation:

```text
app.py                 Streamlit configuration and entry point
ui/                    Session state and dashboard composition
visualization/         Plotly charts and dependency graph rendering
services/              Analysis orchestration and exports
analyzer/              Scanner, AST, Radon, graph, score, and recommendation logic
models/                Typed dataclass contracts shared across layers
tests/                 Unit tests and integration sample projects
```

`AnalysisService` is the single analysis entry point. Analyzer, service, model, and visualization code never imports Streamlit, so the complete analysis core can be tested or reused independently of the dashboard.

## Requirements

- Python 3.12 or newer
- A local Python project to analyze
- Windows, macOS, or Linux

## Installation

Clone the repository and create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running PyAtlas

Start the dashboard from the repository root:

```bash
streamlit run app.py
```

Then:

1. Enter the absolute path to a local Python project.
2. Optionally add project-relative ignore patterns, one per line.
3. Select **Analyze project**.
4. Filter and sort hotspots, select dependency nodes, and inspect module or function details.
5. Download the complete JSON result or hotspot CSV when needed.

Useful ignore-pattern examples:

```text
generated/**
legacy_*.py
examples/vendor/**
```

## Running Tests

Run the complete automated suite:

```bash
pytest -q
```

Compile all application modules as an additional sanity check:

```bash
python -m compileall -q app.py analyzer models services ui visualization
```

## Confusion Score

Confusion Score is a heuristic estimate from 0 to 100. It is intended to guide investigation, not judge code quality.

Function scores combine:

- cyclomatic complexity: 25%
- function length: 20%
- nesting depth: 20%
- parameter count: 10%
- branches: 10%
- local variables: 5%
- function calls: 5%
- nested functions: 5%

Module scores combine function complexity, the largest function risk, capped module length influence, dependency degrees, circular imports, maintainability index, and class structure. Project scores combine a LOC-capped weighted module average (70%), hotspot prevalence (20%), and circular dependency risk (10%).

Every function, class, and module score retains its raw metric, normalized risk, weight, point contribution, and explanation. A large file does not automatically receive a high score because file-size influence is deliberately capped and weighted alongside structural signals.

The local-variable metric counts unique names bound in the function's own scope by assignments, loop targets, context-manager targets, exception handlers, assignment expressions, and structural pattern matching. Parameters, comprehension-only targets, attribute or subscript writes, and bindings inside nested functions, classes, or lambdas are excluded.

Score labels used by the dashboard are:

| Score | Label |
|---:|---|
| 0–20 | Very Easy |
| 21–40 | Easy |
| 41–60 | Moderate |
| 61–80 | Difficult |
| 81–100 | Very Difficult |

## Limitations

- Scores indicate structural risk and cannot understand business context or intentional design trade-offs.
- Static imports may differ from runtime behavior produced through dynamic loading or import hooks.
- Radon and AST analysis target valid Python syntax; invalid files are reported and skipped or partially represented.
- Source preview reads the selected file again, so a file changed after analysis may differ from the recorded metrics.
- Projects containing paths that resolve to the same importable module name, such as `pkg.py` and `pkg/__init__.py`, are rejected with a collision error instead of returning incomplete metrics.
- Analysis is intended for small-to-medium local Python projects; persistent caching is not included in this version.
- Duplicate-code detection is reserved behind a public analyzer interface but intentionally deferred from the MVP.
- PyAtlas currently analyzes Python only and does not inspect Git history, pull requests, or runtime performance.

## Supported Python Versions

PyAtlas requires Python 3.12+. The current automated suite is verified on Python 3.12.

## Roadmap

Potential future extensions include:

- normalized duplicate-function detection
- command-line and CI threshold interfaces
- Git history and changed-file comparison
- before/after refactoring reports
- architecture drift visualization
- public repository analysis
- optional AI-assisted explanations, kept separate from core deterministic analysis

## Safety and Privacy

Analysis runs locally. PyAtlas does not upload source code, call external APIs for core analysis, execute analyzed code, or modify project files.
