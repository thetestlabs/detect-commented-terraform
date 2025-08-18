#!/usr/bin/env python3
"""
Demo script to showcase the detect-commented-terraform functionality.
"""

from pathlib import Path

from detect_commented_terraform.cli import console
from detect_commented_terraform.detector import TerraformCommentDetector


def main() -> None:
    """Run the demo."""
    console.print("🚀 [bold blue]detect-commented-terraform Demo[/bold blue]")
    console.print()

    # Demo the detector
    examples_dir = Path(__file__).parent / "examples"
    detector = TerraformCommentDetector(root_path=examples_dir)

    console.print("📁 Scanning examples directory...")
    result = detector.scan_directory()

    console.print(f"✅ Scanned {result.total_files_scanned} files")
    console.print(f"⚠️  Found {result.total_blocks} commented code blocks in {result.files_with_comments} files")
    console.print()

    console.print("📝 [bold]Commented code blocks found:[/bold]")
    for block in result.blocks:
        console.print(f"  • {block.file_path}:{block.line_range} - {block.first_line[:60]}...")

    console.print()
    console.print("🔧 [bold]How to fix:[/bold]")
    console.print("  1. Review each commented block")
    console.print("  2. Either uncomment the code or remove it entirely")
    console.print("  3. Use version control to track removed code if needed")


if __name__ == "__main__":
    main()
