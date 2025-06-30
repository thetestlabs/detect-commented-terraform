import re
import sys
from typing import List
from pathlib import Path


def is_commented_terraform_line(line: str) -> bool:
    """
    Returns True if the line is a commented-out Terraform code line.
    Matches lines that start with #, //, or /* and contain a Terraform keyword or property pattern.
    """
    KEYWORDS = r"(resource|variable|output|module|provider|data|locals|terraform)"
    PROPERTY_PATTERN = r"(\s*#.*\b\w+\s*=\s*.+|\s*#.*[{}])"
    return bool(
        re.match(r"^\s*(#|//|/\*).*\b" + KEYWORDS + r"\b", line)
        or re.match(PROPERTY_PATTERN, line)
    )


def find_commented_terraform_blocks(lines: List[str]) -> List[int]:
    """
    Returns a list of line numbers (0-based) where a commented-out Terraform block starts.
    """
    block_start_lines = []
    in_block = False
    for i, line in enumerate(lines):
        if re.match(r"^\s*#\s*resource ", line):
            block_start_lines.append(i)
            in_block = True
        elif in_block and re.match(r"^\s*#\s*}\s*$", line):
            in_block = False
    return block_start_lines


def scan_file(filepath: Path) -> List[str]:
    """
    Scan a file for commented-out Terraform code. Returns a list of warning messages.
    """
    warnings = []
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
        for lineno, line in enumerate(lines, 1):
            if is_commented_terraform_line(line):
                warnings.append(
                    f"{filepath}:{lineno}: Commented-out Terraform code detected: {line.rstrip()}"
                )
        # Block detection
        for block_start in find_commented_terraform_blocks(lines):
            warnings.append(
                f"{filepath}:{block_start + 1}: Commented-out Terraform block detected."
            )
        # Detect multi-line /* ... */ block comments containing Terraform code
        in_block_comment = False
        block_comment_lines = []
        for lineno, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("/*"):
                in_block_comment = True
                block_comment_lines = [(lineno, line)]
                if stripped.endswith("*/") and len(stripped) > 4:
                    # Single-line block comment
                    in_block_comment = False
                    block_comment_lines.append((lineno, line))
            elif in_block_comment:
                block_comment_lines.append((lineno, line))
                if "*/" in stripped:
                    # End of block comment
                    if any(
                        is_commented_terraform_line(L)
                        or re.search(
                            r"\b(resource|variable|output|module|provider|data|locals|terraform)\b",
                            L,
                        )
                        for _, L in block_comment_lines
                    ):
                        warnings.append(
                            f"{filepath}:{block_comment_lines[0][0]}: Commented-out Terraform code detected in /* ... */ block comment."
                        )
                    in_block_comment = False
                    block_comment_lines = []
    return warnings


def main() -> None:
    """
    CLI entry point: scan staged .tf files for commented-out Terraform code and block commit if found.
    """
    # Find all .tf files in the repo (for CLI usage)
    tf_files = list(Path.cwd().rglob("*.tf"))
    found = False
    for file in tf_files:
        warnings = scan_file(file)
        for w in warnings:
            print(w)
        if warnings:
            found = True
    if found:
        print("❌ Commented-out Terraform code found.")
        sys.exit(1)
    else:
        print("✅ No commented-out Terraform code found.")
