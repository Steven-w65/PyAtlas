from pathlib import Path

import pytest

from analyzer.project_scanner import ProjectScanner


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_scan_returns_python_files_only(tmp_path: Path) -> None:
    write_file(tmp_path / "alpha.py", "value = 1\n")
    write_file(tmp_path / "nested" / "beta.py", "value = 2\n")
    write_file(tmp_path / "notes.txt", "not Python\n")

    result = ProjectScanner().scan(tmp_path)

    assert [path.relative_to(tmp_path).as_posix() for path in result] == [
        "alpha.py",
        "nested/beta.py",
    ]


def test_scan_ignores_default_directories(tmp_path: Path) -> None:
    write_file(tmp_path / "visible.py")
    write_file(tmp_path / ".venv" / "hidden.py")
    write_file(tmp_path / "__pycache__" / "cached.py")
    write_file(tmp_path / "node_modules" / "vendor.py")

    result = ProjectScanner().scan(tmp_path)

    assert [path.name for path in result] == ["visible.py"]


def test_scan_applies_custom_ignore_patterns(tmp_path: Path) -> None:
    write_file(tmp_path / "keep.py")
    write_file(tmp_path / "generated" / "skip.py")
    write_file(tmp_path / "legacy_module.py")

    scanner = ProjectScanner(
        extra_ignore_patterns=["generated/**", "legacy_*.py"],
    )

    assert [path.name for path in scanner.scan(tmp_path)] == ["keep.py"]


def test_scan_applies_custom_ignored_names(tmp_path: Path) -> None:
    write_file(tmp_path / "keep.py")
    write_file(tmp_path / "private" / "skip.py")

    result = ProjectScanner(ignored_names={"private"}).scan(tmp_path)

    assert [path.name for path in result] == ["keep.py"]


def test_scan_order_is_stable(tmp_path: Path) -> None:
    for relative in ["z.py", "a.py", "nested/c.py", "nested/b.py"]:
        write_file(tmp_path / relative)

    scanner = ProjectScanner()
    first = [path.relative_to(tmp_path).as_posix() for path in scanner.scan(tmp_path)]
    second = [path.relative_to(tmp_path).as_posix() for path in scanner.scan(tmp_path)]

    assert first == second == ["a.py", "nested/b.py", "nested/c.py", "z.py"]


@pytest.mark.parametrize("invalid_name", ["missing", "regular-file"])
def test_scan_rejects_invalid_directory(tmp_path: Path, invalid_name: str) -> None:
    invalid_path = tmp_path / invalid_name
    if invalid_name == "regular-file":
        write_file(invalid_path)

    with pytest.raises(
        ValueError,
        match="Project path does not exist or is not a directory",
    ):
        ProjectScanner().scan(invalid_path)
