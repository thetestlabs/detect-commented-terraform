"""detect-commented-terraform: A CLI tool to detect commented out Terraform code.

This package provides functionality to scan Terraform files and identify
commented out code blocks, reporting their locations and content and
optionally removing those commented out blocks from your codebase.

The main classes are:
    TerraformCommentDetector: The primary scanner for detecting commented code
    CommentedCodeBlock: Data structure representing a found commented block
    DetectionResult: Container for scan results and statistics

Basic Usage:
    >>> from detect_commented_terraform import TerraformCommentDetector
    >>> from pathlib import Path
    >>>
    >>> detector = TerraformCommentDetector(Path("."))
    >>> result = detector.scan_directory(Path("./terraform"))
    >>>
    >>> if result.has_commented_code:
    ...     for block in result.blocks:
    ...         print(f"{block.relative_path}:{block.line_range}")

CLI Usage:
    $ detect-commented-terraform scan --verbose
    $ detect-commented-terraform scan --fix
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Chris McQuaid"
__email__ = "chris@thetestlabs.io"

from .detector import TerraformCommentDetector
from .models import CommentedCodeBlock

__all__ = ["CommentedCodeBlock", "TerraformCommentDetector"]
