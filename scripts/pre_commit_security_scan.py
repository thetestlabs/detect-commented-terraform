#!/usr/bin/env python3
"""Security scanning script for pre-commit hook."""

import re
import sys
from pathlib import Path
from typing import Union


def _read_file_content(file_path: str) -> Union[tuple[str, list[str]], None]:
    """Read file content and return content and lines.

    Args:
        file_path: Path to the file to read

    Returns:
        Tuple of (content, lines) or None if file cannot be read

    """
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
        return content, lines
    except (OSError, UnicodeDecodeError):
        return None


def _check_todo_comments(file_path: str, line_num: int, line: str) -> bool:
    """Check for TODO/FIXME comments.

    Args:
        file_path: Path to the file being checked
        line_num: Line number
        line: Line content

    Returns:
        True if TODO/FIXME found, False otherwise

    """
    if re.search(r"TODO|FIXME|XXX", line, re.IGNORECASE):
        print(f"⚠️  {file_path}:{line_num}: Found TODO/FIXME comment: {line.strip()}")
        return True
    return False


def _check_print_statements(file_path: str, line_num: int, line: str, content: str) -> None:
    """Check for print statements outside __main__ blocks.

    Args:
        file_path: Path to the file being checked
        line_num: Line number
        line: Line content
        content: Full file content

    """
    if "print(" in line and "__main__" not in content:
        print(f"⚠️  {file_path}:{line_num}: Found print statement, consider using logging: {line.strip()}")


def _check_potential_secrets(file_path: str, line_num: int, line: str) -> None:
    """Check for potential secrets in the line.

    Args:
        file_path: Path to the file being checked
        line_num: Line number
        line: Line content

    """
    if (
        re.search(r"password|secret|token|key", line, re.IGNORECASE)
        and not line.strip().startswith("#")
        and not any(word in line.lower() for word in ["test", "example", "placeholder", "dummy"])
    ):
        print(f"⚠️  {file_path}:{line_num}: Potential secret detected: {line.strip()}")


def main() -> int:
    """Scan Python files for security issues."""
    issues_found = False

    for file_path in sys.argv[1:]:
        if "test_" in Path(file_path).name:
            continue

        file_content = _read_file_content(file_path)
        if file_content is None:
            continue

        content, lines = file_content

        for i, line in enumerate(lines, 1):
            # Check for TODO/FIXME comments
            if _check_todo_comments(file_path, i, line):
                issues_found = True

            # Check for print statements (exclude __main__ blocks)
            _check_print_statements(file_path, i, line, content)

            # Check for potential secrets
            _check_potential_secrets(file_path, i, line)

    if issues_found:
        print("Note: TODO/FIXME comments found but not blocking commit")

    return 0


if __name__ == "__main__":
    sys.exit(main())
