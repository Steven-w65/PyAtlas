# 🗺️ PyAtlas

**A local, interactive Python codebase analyzer for complexity, dependencies, circular imports, structural hotspots, and maintainability risk.**

PyAtlas turns static-analysis metrics into a navigable dashboard so you can quickly understand **where complexity lives, why it matters, and what deserves attention first**.

Instead of showing disconnected numbers, PyAtlas combines structural metrics into an explainable **Confusion Score** and preserves the contribution of every underlying signal.

> **Local-first by design:** PyAtlas analyzes source code on your machine, does not execute analyzed projects, and does not require internet access after installation.

---

## ✨ What PyAtlas Helps You Answer

- 🔥 Which modules and functions deserve review first?
- 🧠 Why did a symbol receive a high Confusion Score?
- 🔗 Where are dependencies concentrated?
- 🔄 Which imports form circular dependency groups?
- 🌲 Which functions have deep nesting?
- 📈 Where is cyclomatic complexity highest?
- 🧩 Which parts of the project create the most structural risk?

---

## 📸 Screenshot

> **Dashboard screenshot placeholder**
>
> Run PyAtlas against a project and capture:
>
> - the project overview
> - the dependency map
> - the module/function detail inspector

---

## 🚀 Features

### 🔎 Code Discovery & Parsing

- Recursive `.py` file discovery
- Safe default ignore rules
- Custom project-relative glob patterns
- AST extraction for:
  - synchronous functions
  - asynchronous functions
  - nested functions
  - class methods
- Partial analysis when individual files contain syntax, encoding, or permission errors

### 🧠 Function-Level Analysis

PyAtlas captures:

- function spans
- parameter counts
- branches
- loops
- nesting depth
- function calls
- return statements
- `try` blocks
- local-variable counts
- nested functions

PyAtlas also integrates:

- **Radon cyclomatic complexity**
- **Radon maintainability index**

### 🔗 Dependency Analysis

PyAtlas builds an internal dependency graph with:

- fan-in
- fan-out
- isolated modules
- circular dependency groups
- relationship highlighting
- dependency-risk inspection

### 📊 Explainable Confusion Scores

Scores are available at the:

- function level
- class level
- module level
- project level

Every score preserves:

- raw metric values
- normalized risk
- metric weight
- point contribution
- human-readable explanation

### 📈 Dashboard & Visualization

- Sortable and filterable hotspot table
- Complexity charts
- Score-distribution charts
- File-size charts
- Dependency-risk charts
- Interactive dependency map
- Module selection
- Relationship highlighting
- Module detail inspector
- Function detail inspector
- Source previews

### 📤 Recommendations & Export

PyAtlas provides advisory recommendations for code that is:

- unusually large
- deeply nested
- highly complex
- highly connected

Exports include:

- complete analysis as JSON
- hotspot results as CSV

---

## 🏗️ Architecture

PyAtlas keeps **analysis logic separate from presentation**.

```text
app.py                 Streamlit configuration and entry point
ui/                    Session state and dashboard composition
visualization/         Plotly charts and dependency graph rendering
services/              Analysis orchestration and exports
analyzer/              Scanner, AST, Radon, graph, score, and recommendation logic
models/                Typed dataclass contracts shared across layers
tests/                 Unit tests and integration sample projects
```

`AnalysisService` is the single entry point for analysis.

The analyzer, service, model, and visualization layers **do not import Streamlit**, which keeps the analysis core reusable and independently testable.

---

## 📋 Requirements

Before installing PyAtlas, make sure you have:

- **Python 3.12 or newer**
- `pip`
- A local Python project to analyze
- Windows, macOS, or Linux

Check your Python version:

```bash
python --version
```

On some systems, you may need:

```bash
python3 --version
```

---

## 📦 Installation

### 1. Clone the Repository

Clone PyAtlas from GitHub:

```bash
git clone <repository-url>
```

Move into the project directory:

```bash
cd PyAtlas
```

Replace `<repository-url>` with the actual GitHub repository URL.

---

### 2. Create a Virtual Environment

Create a local virtual environment:

```bash
python -m venv .venv
```

On systems where Python is available as `python3`, use:

```bash
python3 -m venv .venv
```

Using a virtual environment keeps PyAtlas dependencies isolated from your global Python installation.

---

### 3. Activate the Virtual Environment

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

#### Windows Command Prompt

```cmd
.venv\Scripts\activate.bat
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

After activation, your terminal should usually display something similar to:

```text
(.venv)
```

---

### 4. Upgrade `pip`

Before installing project dependencies, upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

This helps avoid installation issues caused by an outdated package installer.

---

### 5. Install `requirements.txt`

PyAtlas dependencies are listed in:

```text
requirements.txt
```

Install them with:

```bash
pip install -r requirements.txt
```

This command reads every dependency listed in `requirements.txt` and installs the required versions into the active virtual environment.

You can also use:

```bash
python -m pip install -r requirements.txt
```

---

### 6. Verify the Installation

View the installed packages:

```bash
pip list
```

You can also verify that Streamlit is installed:

```bash
streamlit --version
```

Or:

```bash
python -m streamlit --version
```

---

### 7. Updating Dependencies

If `requirements.txt` changes after you pull a newer version of PyAtlas, run:

```bash
pip install -r requirements.txt
```

again.

To upgrade packages while respecting the versions defined in `requirements.txt`:

```bash
pip install --upgrade -r requirements.txt
```

---

### 8. Creating or Updating `requirements.txt`

If you add new dependencies during development, install them normally:

```bash
pip install package-name
```

Then regenerate the dependency file:

```bash
pip freeze > requirements.txt
```

> **Note:** `pip freeze` records every installed package in the active environment. Review the generated file before committing it to avoid including unrelated development packages.

---

## ▶️ Running PyAtlas

Make sure the virtual environment is active.

From the repository root, run:

```bash
streamlit run app.py
```

You can also run Streamlit through Python:

```bash
python -m streamlit run app.py
```

Streamlit will start a local development server and open the PyAtlas dashboard in your browser.

---

## 🧭 Using PyAtlas

Once the dashboard is running:

1. Enter the **absolute path** to a local Python project.
2. Optionally add project-relative ignore patterns, one per line.
3. Select **Analyze project**.
4. Review the project overview.
5. Filter and sort hotspots.
6. Select dependency nodes to inspect relationships.
7. Inspect individual modules or functions.
8. Review Confusion Score explanations.
9. Export the complete analysis as JSON or hotspot results as CSV.

---

## 🚫 Ignore Patterns

PyAtlas supports project-relative ignore patterns.

Example:

```text
generated/**
legacy_*.py
examples/vendor/**
```

These patterns can be useful for excluding:

- generated code
- vendor directories
- experimental files
- legacy modules
- third-party source copied into the project

---

## 🧪 Running Tests

Run the complete automated test suite:

```bash
pytest -q
```

If `pytest` is installed inside the virtual environment, you can also use:

```bash
python -m pytest -q
```

---

## ✅ Compile Sanity Check

Compile the application modules to check for basic Python syntax and import-time compilation issues:

```bash
python -m compileall -q app.py analyzer models services ui visualization
```

A successful command with no output indicates that compilation completed without errors.

---

## 🧠 Confusion Score

**Confusion Score** is a heuristic estimate from **0 to 100**.

It is designed to guide investigation—not to judge code quality.

A high score means that several structural signals suggest a symbol may require more cognitive effort to understand, review, or maintain.

---

## ⚙️ Function Score Weights

Function scores combine the following metrics:

| Metric | Weight |
|---|---:|
| Cyclomatic complexity | 25% |
| Function length | 20% |
| Nesting depth | 20% |
| Parameter count | 10% |
| Branches | 10% |
| Local variables | 5% |
| Function calls | 5% |
| Nested functions | 5% |

The final result is normalized to a score between `0` and `100`.

---

## 📦 Module Scores

Module scores combine:

- function complexity
- largest-function risk
- capped module-length influence
- dependency degrees
- circular imports
- maintainability index
- class structure

File size is deliberately capped so a large module does not automatically receive a high score.

---

## 🌍 Project Scores

Project scores combine:

| Component | Weight |
|---|---:|
| LOC-capped weighted module average | 70% |
| Hotspot prevalence | 20% |
| Circular dependency risk | 10% |

This provides a project-wide structural-risk estimate while preventing large files from dominating the result.

---

## 🔍 Score Explainability

Every function, class, and module score retains the information used to calculate it.

For every metric, PyAtlas stores:

```text
Raw Metric
    ↓
Normalized Risk
    ↓
Weight
    ↓
Point Contribution
    ↓
Explanation
```

This makes the scoring system inspectable rather than opaque.

Instead of only seeing:

```text
Confusion Score: 78
```

developers can inspect **why** the score reached that value.

---

## 🧮 Local-Variable Counting

The local-variable metric counts **unique names bound within the function's own scope**.

### Included

Bindings created through:

- assignments
- loop targets
- context-manager targets
- exception handlers
- assignment expressions
- structural pattern matching

### Excluded

The following are not counted:

- parameters
- comprehension-only targets
- attribute writes
- subscript writes
- bindings inside nested functions
- bindings inside nested classes
- bindings inside lambdas

---

## 🎚️ Score Labels

| Score | Label |
|---:|---|
| `0–20` | 🟢 Very Easy |
| `21–40` | 🟢 Easy |
| `41–60` | 🟡 Moderate |
| `61–80` | 🟠 Difficult |
| `81–100` | 🔴 Very Difficult |

These labels provide a quick visual interpretation of structural risk.

---

## 🔄 Dependency Analysis

PyAtlas builds an internal module dependency graph based on static imports.

The graph can reveal:

- modules with high fan-in
- modules with high fan-out
- isolated modules
- tightly connected areas
- circular dependency groups
- structural concentration points

The interactive dashboard allows developers to select modules and inspect their relationships.

---

## 🔁 Circular Imports

Circular dependency groups occur when modules depend on each other directly or indirectly.

For example:

```text
module_a
   ↓
module_b
   ↓
module_c
   ↓
module_a
```

PyAtlas identifies these groups and includes them as part of module and project-level risk analysis.

---

## 📊 Dashboard Views

PyAtlas provides several visual tools for exploring analysis results.

### Project Overview

Displays high-level metrics such as:

- project Confusion Score
- analyzed modules
- function counts
- project size
- hotspot prevalence
- circular dependency risk

### Hotspot Table

A sortable and filterable table for locating high-risk:

- functions
- classes
- modules

### Complexity Charts

Visualize how complexity is distributed across the project.

### Score Distribution

Shows how Confusion Scores are distributed between low-risk and high-risk code.

### File-Size Analysis

Highlights unusually large modules while keeping size separate from other structural signals.

### Dependency Risk

Visualizes modules with concentrated incoming or outgoing dependencies.

### Dependency Map

An interactive graph for exploring module relationships.

### Detail Inspector

Inspect:

- module metrics
- function metrics
- Confusion Score contributions
- recommendations
- source previews

---

## 💡 Recommendations

PyAtlas produces advisory recommendations for structural patterns that may deserve review.

Examples include:

- unusually long functions
- deep nesting
- high cyclomatic complexity
- excessive parameter counts
- highly connected modules
- circular imports
- unusually large modules

Recommendations are intended as **review prompts**, not automatic refactoring instructions.

---

## 📤 Exporting Results

PyAtlas supports two primary export formats.

### JSON Export

The complete analysis result can be exported as JSON.

This is useful for:

- custom tooling
- archival analysis
- further data processing
- integration with future CLI or CI workflows

### CSV Export

Hotspots can be exported as CSV.

This is useful for:

- spreadsheet analysis
- reporting
- team review
- prioritization workflows

---

## 🔐 Safety & Privacy

PyAtlas is designed as a **local inspection tool**.

It does **not**:

- upload source code
- send analyzed code to external APIs
- execute analyzed project code
- modify analyzed source files
- require an internet connection for core analysis after installation

Analysis runs locally on your machine.

---

## ⚠️ Limitations

PyAtlas intentionally focuses on deterministic structural analysis.

Current limitations include:

- Scores indicate structural risk and cannot understand business context or intentional architectural trade-offs.
- Static imports may differ from runtime behavior caused by dynamic loading or import hooks.
- Radon and AST analysis require valid Python syntax.
- Invalid files are reported and skipped or partially represented.
- Source previews read the selected file again, so a file modified after analysis may differ from the recorded metrics.
- Projects containing paths that resolve to the same importable module name, such as `pkg.py` and `pkg/__init__.py`, are rejected with a collision error instead of returning incomplete metrics.
- PyAtlas is intended primarily for small-to-medium local Python projects.
- Persistent analysis caching is not included in the current version.
- Duplicate-code detection has a public analyzer interface but is intentionally deferred from the MVP.
- PyAtlas currently analyzes Python only.
- Git history is not analyzed.
- Pull requests are not analyzed.
- Runtime performance is not measured.

---

## 🐍 Supported Python Versions

PyAtlas requires:

```text
Python 3.12+
```

The current automated test suite is verified on:

```text
Python 3.12
```

---

## 🛣️ Roadmap

Potential future extensions include:

- [ ] Normalized duplicate-function detection
- [ ] Command-line interface
- [ ] CI threshold checks
- [ ] Git history analysis
- [ ] Changed-file comparison
- [ ] Before/after refactoring reports
- [ ] Architecture drift visualization
- [ ] Public repository analysis
- [ ] Persistent analysis caching
- [ ] Historical score tracking
- [ ] Optional AI-assisted explanations

Any AI-assisted functionality will remain separate from PyAtlas's deterministic core analysis.

---

## 🎯 Design Philosophy

### Explainability Over Mystery

Every score should show where it came from.

### Inspection Over Judgment

Metrics identify places worth investigating. They do not decide whether code is inherently “good” or “bad.”

### Local-First Analysis

Your source code stays on your machine.

### Separation of Concerns

Analysis should remain reusable independently of the dashboard.

### Partial Results Over Total Failure

A problematic file should not prevent useful analysis of the rest of the project.

### Deterministic Core

Core analysis should remain reproducible and independent of external AI or cloud services.

---

## 🗺️ How PyAtlas Works

```text
Python Project
      │
      ▼
 File Discovery
      │
      ▼
 AST Parsing
      │
      ├───────────────┐
      ▼               ▼
Structural Metrics   Radon Metrics
      │               │
      └───────┬───────┘
              ▼
      Dependency Graph
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
   Fan-In   Fan-Out   Cycles
      │       │        │
      └───────┼────────┘
              ▼
       Confusion Scores
              │
              ▼
        Recommendations
              │
              ▼
      Interactive Dashboard
              │
      ┌───────┼──────────┐
      ▼       ▼          ▼
   Hotspots  Graph    Inspectors
```

---

## 📁 Example Project Structure

A typical PyAtlas repository may look like:

```text
PyAtlas/
├── app.py
├── requirements.txt
├── analyzer/
│   ├── scanner.py
│   ├── ast_analyzer.py
│   ├── radon_analyzer.py
│   ├── dependency_graph.py
│   ├── scoring.py
│   └── recommendations.py
├── models/
│   └── ...
├── services/
│   └── ...
├── ui/
│   └── ...
├── visualization/
│   └── ...
└── tests/
    └── ...
```

The exact structure may evolve as the project grows.

---

## 🛠️ Development Workflow

A typical development workflow is:

```bash
git clone <repository-url>
cd PyAtlas
python -m venv .venv
```

Activate the environment.

Then install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run tests:

```bash
pytest -q
```

Run the compile check:

```bash
python -m compileall -q app.py analyzer models services ui visualization
```

Start the dashboard:

```bash
streamlit run app.py
```

---

## 🧹 Deactivating the Virtual Environment

When you are finished working with PyAtlas, deactivate the environment with:

```bash
deactivate
```

---

## ❓ Common Installation Issues

### `python` Is Not Recognized

Try:

```bash
python3 --version
```

and use `python3` instead of `python`.

---

### `pip` Is Not Recognized

Use:

```bash
python -m pip install -r requirements.txt
```

instead of:

```bash
pip install -r requirements.txt
```

---

### `streamlit` Is Not Recognized

Make sure your virtual environment is active.

Then try:

```bash
python -m streamlit run app.py
```

---

### PowerShell Blocks Virtual Environment Activation

Windows PowerShell may prevent local scripts from running.

You can inspect the current policy with:

```powershell
Get-ExecutionPolicy
```

If your system policy allows it, you may enable locally created scripts for your user account:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

Only change execution policies if you understand your system's security requirements.

---

### Dependency Installation Fails

First upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

Then retry:

```bash
python -m pip install -r requirements.txt
```

Also confirm that you are running Python 3.12 or newer:

```bash
python --version
```

---

## 🤝 Contributing

Contributions are welcome.

A typical contribution workflow is:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Add or update tests.
5. Run the full test suite.
6. Run the compile sanity check.
7. Submit a pull request.

Before submitting changes, verify:

```bash
pytest -q
```

and:

```bash
python -m compileall -q app.py analyzer models services ui visualization
```

---

## 📌 Project Status

PyAtlas is focused on providing an explainable, deterministic, local-first view of Python codebase structure.

The current version prioritizes:

- maintainable architecture
- structural metrics
- explainable scoring
- interactive visualization
- safe local inspection
- useful partial results

Future versions may expand into CI, Git analysis, historical comparisons, and optional AI-assisted explanation layers.

---

## 🗺️ In Short

PyAtlas turns a Python codebase into an interactive structural map.

It helps you:

- **find hotspots**
- **understand complexity**
- **trace dependencies**
- **detect circular imports**
- **inspect risky functions**
- **see why a score is high**
- **prioritize what to review first**

Use PyAtlas to find the parts of a codebase that deserve attention—and understand **why they stand out**.