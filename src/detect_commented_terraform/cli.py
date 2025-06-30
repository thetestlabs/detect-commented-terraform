import re
import sys
from typing import List
from pathlib import Path
from rich.console import Console


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


def scan_file(filepath: Path, repo_root: Path | None = None) -> list[dict]:
    """
    Scan a file for commented-out Terraform code. Returns a list of warning dicts.
    """
    warnings = []
    if repo_root is None:
        # Try to find the repo root (directory containing .git or project root)
        repo_root = Path.cwd()
        for parent in filepath.parents:
            if (parent / ".git").exists():
                repo_root = parent
                break
    rel_path = filepath.relative_to(repo_root)
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
        for lineno, line in enumerate(lines, 1):
            if is_commented_terraform_line(line):
                # Find the first line of the block (if inside a block)
                block_start = lineno
                for i in range(lineno - 1, 0, -1):
                    if lines[i - 1].strip().startswith(
                        ("# resource", "# module", "# data", "# provider")
                    ):
                        block_start = i
                        break
                warnings.append(
                    {
                        "file": str(rel_path),
                        "line": lineno,
                        "block_start": block_start,
                        "block_first_line": lines[block_start - 1].rstrip(),
                        "line_content": line.rstrip(),
                    }
                )
        # Block detection
        for block_start in find_commented_terraform_blocks(lines):
            warnings.append(
                {
                    "file": str(rel_path),
                    "line": block_start + 1,
                    "block_start": block_start + 1,
                    "block_first_line": lines[block_start].rstrip(),
                    "line_content": lines[block_start].rstrip(),
                }
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
                    in_block_comment = False
                    block_comment_lines.append((lineno, line))
            elif in_block_comment:
                block_comment_lines.append((lineno, line))
                if "*/" in stripped:
                    if any(
                        is_commented_terraform_line(L)
                        or re.search(
                            r"\b(resource|variable|output|module|provider|data|locals|terraform)\b",
                            L,
                        )
                        for _, L in block_comment_lines
                    ):
                        first_lineno, first_line = block_comment_lines[0]
                        warnings.append(
                            {
                                "file": str(rel_path),
                                "line": first_lineno,
                                "block_start": first_lineno,
                                "block_first_line": first_line.rstrip(),
                                "line_content": "/* ... */ block comment",
                            }
                        )
                    in_block_comment = False
                    block_comment_lines = []
    return warnings


def main() -> None:
    """
    CLI entry point: scan staged .tf files for commented-out Terraform code and block commit if found.
    """
    console = Console()
    tf_files = list(Path.cwd().rglob("*.tf"))
    found = False
    for file in tf_files:
        warnings = scan_file(file)
        for w in warnings:
            console.print(
                f"[bold red]Commented-out Terraform code detected[/bold red] in "
                f"[bold yellow]{w['file']}[/bold yellow] at line [bold cyan]{w['line']}[/bold cyan]:\n"
                f"    [dim]{w['block_first_line']}[/dim]",
                markup=True,
            )
        if warnings:
            found = True
    if found:
        console.print("[bold red]❌ Commented-out Terraform code found.[/bold red]", markup=True)
        sys.exit(1)
    else:
        console.print("[bold green]✅ No commented-out Terraform code found.[/bold green]", markup=True)
