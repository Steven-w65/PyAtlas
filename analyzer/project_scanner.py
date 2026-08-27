"""Safe, deterministic discovery of Python source files."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath


DEFAULT_IGNORED_NAMES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
}


class ProjectScanner:
    """Discover Python files below a project root without following symlinks."""

    def __init__(
        self,
        ignored_names: set[str] | None = None,
        extra_ignore_patterns: list[str] | None = None,
    ) -> None:
        self.ignored_names = DEFAULT_IGNORED_NAMES | (ignored_names or set())
        self.extra_ignore_patterns = tuple(extra_ignore_patterns or ())
        self.errors: list[str] = []

    def scan(self, project_path: str | Path) -> list[Path]:
        """Return stable, sorted Python paths under *project_path*.

        Inaccessible entries are recorded in ``errors`` and skipped. An invalid
        project root is the only fatal scanner condition.
        """

        root = Path(project_path)
        if not root.exists() or not root.is_dir():
            raise ValueError("Project path does not exist or is not a directory.")

        self.errors = []
        discovered: list[Path] = []
        self._scan_directory(root, root, discovered)
        return sorted(discovered, key=lambda path: path.relative_to(root).as_posix())

    def _scan_directory(
        self,
        root: Path,
        directory: Path,
        discovered: list[Path],
    ) -> None:
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name.casefold())
        except OSError as exc:
            self.errors.append(self._format_error(directory, exc))
            return

        for entry in entries:
            path = Path(entry.path)
            relative = path.relative_to(root).as_posix()
            if entry.name in self.ignored_names or self._matches_pattern(relative):
                continue
            try:
                if entry.is_dir(follow_symlinks=False):
                    if not entry.is_symlink():
                        self._scan_directory(root, path, discovered)
                elif entry.is_file(follow_symlinks=False) and path.suffix == ".py":
                    discovered.append(path)
            except OSError as exc:
                self.errors.append(self._format_error(path, exc))

    def _matches_pattern(self, relative_path: str) -> bool:
        candidate = PurePosixPath(relative_path)
        return any(candidate.match(pattern) for pattern in self.extra_ignore_patterns)

    @staticmethod
    def _format_error(path: Path, exc: OSError) -> str:
        return f"{path}: {type(exc).__name__}: {exc}"

