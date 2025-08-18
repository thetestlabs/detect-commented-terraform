"""Pre-commit hook functionality for detect-commented-terraform."""

import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from .detector import TerraformCommentDetector


def _filter_terraform_files(filenames: Sequence[str]) -> list[Path]:
    """Filter and resolve Terraform files from the given filenames.

    Args:
        filenames: List of filenames to filter

    Returns:
        List of resolved Path objects for Terraform files

    """
    return [Path(f).resolve() for f in filenames if f.endswith((".tf", ".tfvars"))]


def _process_terraform_files(terraform_files: list[Path], detector: TerraformCommentDetector) -> list[Any]:
    """Process Terraform files and collect commented blocks.

    Args:
        terraform_files: List of Terraform files to process
        detector: TerraformCommentDetector instance

    Returns:
        List of all commented blocks found

    """
    all_blocks: list[Any] = []

    for tf_file in terraform_files:
        if tf_file.exists():
            try:
                blocks = detector.find_commented_blocks(tf_file)
                all_blocks.extend(blocks)
            except (OSError, UnicodeDecodeError, PermissionError) as e:
                # Log error but continue processing other files
                logger.warning(f"Error processing {tf_file}: {e}")
                continue

    return all_blocks


def run_pre_commit_hook(filenames: Sequence[str], root_path: Optional[Path] = None) -> int:
    """Run the pre-commit hook on the given files.

    Args:
        filenames: List of filenames to check
        root_path: Root path of the repository

    Returns:
        Exit code: 0 if no issues found, 1 if commented code found

    """
    if not filenames:
        return 0

    terraform_files = _filter_terraform_files(filenames)
    if not terraform_files:
        return 0

    root = root_path or Path.cwd()
    detector = TerraformCommentDetector(root_path=root)
    all_blocks = _process_terraform_files(terraform_files, detector)

    if all_blocks:
        print(f"❌ Found {len(all_blocks)} commented Terraform code block(s):")
        for block in all_blocks:
            print(f"  {block}")
        return 1

    return 0


def main() -> None:
    """Run the pre-commit hook entry point."""
    # Configure minimal logging for pre-commit
    logger.remove()
    logger.add(sys.stderr, format="<level>{message}</level>", level="WARNING")

    # Pre-commit passes filenames as arguments
    exit_code = run_pre_commit_hook(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
