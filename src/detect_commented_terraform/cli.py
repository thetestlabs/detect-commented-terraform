import re
import sys
from typing import List
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console

app = typer.Typer(help="Detect commented-out Terraform code in .tf files.")


def is_commented_terraform_line(line: str) -> bool:
    """
    Returns True if the line is a commented-out Terraform code line.
    Matches lines that start with #, //, or /* and contain a Terraform keyword or property pattern.
    """
    keywords = r"(resource|variable|output|module|provider|data|locals|terraform)"
    property_pattern = r"(\s*#.*\b\w+\s*=\s*.+|\s*#.*[{}])"
    return bool(
        re.match(r"^\s*(#|//|/\*).*\b" + keywords + r"\b", line) or re.match(property_pattern, line)
    )


def find_commented_terraform_blocks(lines: List[str]) -> list[tuple[int, int]]:
    """
    Returns a list of (start_line, end_line) tuples (0-based) for commented-out Terraform blocks.
    Detects blocks for resource, variable, output, module, provider, data, locals, terraform.
    Also detects single-line commented-out blocks (e.g., # data ... {}).
    """
    blocks = []
    in_block = False
    block_start = None
    # Regex for all Terraform block types
    block_types = r"resource|variable|output|module|provider|data|locals|terraform"
    block_start_re = re.compile(rf"^\s*#\s*({block_types})\b.*\{{\s*$")
    single_line_block_re = re.compile(rf"^\s*#\s*({block_types})\b.*\{{.*}}\s*$")
    for i, line in enumerate(lines):
        if single_line_block_re.match(line):
            blocks.append((i, i))
        elif block_start_re.match(line):
            in_block = True
            block_start = i
        elif in_block and re.match(r"^\s*#\s*}\s*$", line):
            if block_start is not None:  # Ensure block_start is not None
                blocks.append((block_start, i))
            in_block = False
            block_start = None
    return blocks


def scan_file(filepath: Path, repo_root: Path | None = None) -> list[dict]:
    """
    Scan a file for commented-out Terraform code. Returns a list of warning dicts.
    Only detects entire commented-out blocks, not single lines.
    """
    warnings: list[dict] = []
    if repo_root is None:
        # Try to find the repo root (directory containing .git or project root)
        repo_root = Path.cwd()
        for parent in filepath.parents:
            if (parent / ".git").exists():
                repo_root = parent
                break
    rel_path = filepath.relative_to(repo_root)
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        logger.warning(f"Error reading {filepath}: {e}")
        return warnings
    # Only block detection (ignore single lines)
    for block_start, block_end in find_commented_terraform_blocks(lines):
        warnings.append(
            {
                "file": str(rel_path),
                "line_range": (block_start + 1, block_end + 1),
                "block_start": block_start + 1,
                "block_end": block_end + 1,
                "block_first_line": lines[block_start].rstrip(),
                "block_last_line": lines[block_end].rstrip(),
                "line_content": f"{lines[block_start].rstrip()} ... {lines[block_end].rstrip()}",
            }
        )
    # Optionally, keep multi-line /* ... */ block detection if desired
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


def main(
    files: list[str] = typer.Argument(
        None, help="Terraform files to scan (default: all .tf files)"
    ),
) -> None:
    """
    CLI entry point: scan .tf files for commented-out Terraform code and block commit if found.
    Accepts file paths as arguments (for pre-commit), or scans all .tf files if none given.
    """
    console = Console()
    logger.remove()  # Remove default stderr logger
    logger.add(sys.stderr, level="WARNING")  # Only show warnings/errors by default
    if files:
        tf_files = {str(Path(f).resolve()) for f in files if f.endswith(".tf")}
    else:
        tf_files = {str(p.resolve()) for p in Path.cwd().rglob("*.tf")}
    found = False
    already_reported = set()
    for file_path in tf_files:
        file = Path(file_path)
        try:
            warnings = scan_file(file)
        except OSError as e:
            logger.error(f"Failed to scan {file}: {e}")
            continue
        for w in warnings:
            if "line_range" in w:
                key = (w["file"], w["block_start"], w["block_end"])
                if key in already_reported:
                    continue
                already_reported.add(key)
                console.print(
                    f"[bold red]Commented-out Terraform block detected[/bold red] in "
                    f"[bold yellow]{w['file']}[/bold yellow] at lines [bold cyan]{w['block_start']} - {w['block_end']}[/bold cyan]:\n"
                    f"    [dim]{w['block_first_line']} ... {w['block_last_line']}[/dim]",
                    markup=True,
                )
                found = True
    if found:
        raise typer.Exit(code=1)
    # No output if no commented-out code found


@app.command()
def cli(
    files: list[str] = typer.Argument(
        None, help="Terraform files to scan (default: all .tf files)"
    ),
):
    """Detect commented-out Terraform code in .tf files."""
    main(files)


if __name__ == "__main__":
    app()
