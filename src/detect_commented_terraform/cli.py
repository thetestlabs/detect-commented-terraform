"""CLI interface for the detect-commented-terraform tool."""

import sys
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from . import __version__
from .detector import TerraformCommentDetector
from .models import DetectionResult

app = typer.Typer(
    name="detect-commented-terraform",
    help="Detect and optionally remove commented out Terraform/OpenTofu/Terragrunt Code",
    no_args_is_help=False,
    invoke_without_command=True,
)

console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    logger.remove()  # Remove default handler

    if verbose:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>",
            level="DEBUG",
        )
    else:
        logger.add(
            sys.stderr,
            format="<level>{level}</level>: <level>{message}</level>",
            level="INFO",
        )


def format_results(result: DetectionResult, fixed_count: int = 0) -> None:
    """Format and display the detection results."""
    if not result.has_commented_code:
        console.print("✅ No commented Terraform code found!", style="green")
        return

    if fixed_count > 0:
        console.print(f"🔧 Fixed {fixed_count} commented code block(s)!", style="green")
        console.print()
    else:
        console.print(
            f"❌ Found {result.total_blocks} commented code block(s) in {result.files_with_comments} file(s)",
            style="red",
        )
        console.print()

    # Create a table for the results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File", style="cyan")
    table.add_column("Line(s)", style="yellow")
    table.add_column("First Line", style="white")

    for block in result.blocks:
        table.add_row(
            str(block.file_path),
            block.line_range,
            (block.first_line[:80] + "..." if len(block.first_line) > 80 else block.first_line),
        )

    console.print(table)


@app.callback()
def main_callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    show_version: bool = typer.Option(False, "--version", help="Show version information"),
) -> None:
    """Detect and optionally remove commented out Terraform, OpenTofu, and Terragrunt code.

    This tool scans Terraform/OpenTofu/Terragrunt files (.tf, .tofu, .tfvars, .hcl) for commented-out
    code blocks and can optionally remove them. It's designed to help keep your IaC
    codebase clean and maintainable.

    Supported formats:
    - Terraform (.tf, .tfvars)
    - OpenTofu (.tf, .tofu, .tfvars)
    - Terragrunt (.hcl)

    Examples:
      detect-commented-terraform scan                    # Scan current directory
      detect-commented-terraform scan /path/to/terraform # Scan specific directory
      detect-commented-terraform scan --fix              # Remove found blocks
      detect-commented-terraform scan -f                 # Remove found blocks (short)
      detect-commented-terraform scan --verbose          # Show detailed output

    """
    if show_version:
        console.print(f"detect-commented-terraform {__version__}")
        raise typer.Exit()

    if verbose:
        setup_logging(verbose)

    # If no subcommand is provided and no version flag, show help
    if ctx.invoked_subcommand is None and not show_version:
        ctx.get_help()
        console.print("\n💡 Use 'detect-commented-terraform scan' to scan for commented IaC code")
        console.print("   Add --fix or -f to automatically remove found blocks")
        console.print("   Supports Terraform, OpenTofu, and Terragrunt files")
        raise typer.Exit()


def _validate_scan_path(scan_path: Path) -> None:
    """Validate that the scan path exists and is a directory.

    Args:
        scan_path: Path to validate

    Raises:
        typer.Exit: If path doesn't exist or isn't a directory

    """
    if not scan_path.exists():
        console.print(f"❌ Path does not exist: {scan_path}", style="red")
        raise typer.Exit(code=1)

    if not scan_path.is_dir():
        console.print(f"❌ Path is not a directory: {scan_path}", style="red")
        raise typer.Exit(code=1)


def _handle_fix_operation(detector: TerraformCommentDetector, result: DetectionResult) -> int:
    """Handle the fix operation with user confirmation.

    Args:
        detector: TerraformCommentDetector instance
        result: Detection result containing blocks to fix

    Returns:
        Number of blocks fixed

    Raises:
        typer.Exit: If user cancels the operation

    """
    if not typer.confirm(f"Are you sure you want to remove {result.total_blocks} commented code block(s)?"):
        console.print("❌ Operation cancelled", style="yellow")
        raise typer.Exit(code=1)

    return detector.fix_commented_blocks(result.blocks)


def scan_terraform(
    path: Optional[Path],
    verbose: bool,
    fix: bool,
    exit_code: bool,
) -> None:
    """Core scanning functionality extracted for reuse."""
    setup_logging(verbose)

    scan_path = path or Path.cwd()
    _validate_scan_path(scan_path)

    detector = TerraformCommentDetector(root_path=scan_path)
    result = detector.scan_directory()

    fixed_count = 0
    if fix and result.has_commented_code:
        fixed_count = _handle_fix_operation(detector, result)
        # Re-scan to show the results after fixing
        result = detector.scan_directory()

    format_results(result, fixed_count)

    if exit_code and result.has_commented_code and not fix:
        raise typer.Exit(code=1)


@app.command()
def scan(
    path: Optional[Path] = typer.Argument(  # noqa: B008
        None, help="Path to scan for Terraform/OpenTofu/Terragrunt files (defaults to current directory)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    fix: bool = typer.Option(
        False, "--fix", "-f", help="Automatically remove commented out Terraform/OpenTofu/Terragrunt code"
    ),
    exit_code: bool = typer.Option(
        True,
        "--exit-code/--no-exit-code",
        help="Exit with code 1 if commented code is found (useful for CI/CD)",
    ),
) -> None:
    """Scan for commented out Terraform/OpenTofu/Terragrunt code. Use --fix/-f to automatically remove found blocks."""
    scan_terraform(path, verbose, fix, exit_code)


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"detect-commented-terraform {__version__}")


def main() -> None:
    """Run the main CLI application."""
    app()


if __name__ == "__main__":
    main()
