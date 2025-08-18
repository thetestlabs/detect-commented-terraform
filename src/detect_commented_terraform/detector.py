"""Terraform comment detection logic."""

import re
from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar, Optional

from loguru import logger

from .models import CommentedCodeBlock, DetectionResult


class TerraformCommentDetector:
    """Detects commented out Terraform, OpenTofu, and Terragrunt code in files.

    This class scans Terraform/OpenTofu/Terragrunt code files (.tf, .tfvars, .hcl) to identify
    commented-out code blocks that appear to be legitimate configuration rather than
    documentation comments. Supports Terraform, OpenTofu, and Terragrunt syntax.

    Args:
        root_path (Optional[Path]): The root directory to use for relative path
            calculations. Defaults to current working directory if not provided.

    Examples:
        Basic usage:

        >>> from pathlib import Path
        >>> detector = TerraformCommentDetector(Path("/my/terraform/project"))
        >>> result = detector.scan_directory(Path("./modules"))
        >>> print(f"Found {result.total_blocks} commented blocks")

        Scanning a single file:

        >>> blocks = list(detector.scan_file(Path("main.tf")))
        >>> for block in blocks:
        ...     print(f"{block.relative_path}:{block.line_range}")

    Attributes:
        TERRAFORM_KEYWORDS (ClassVar[set[str]]): Set of Terraform/OpenTofu/Terragrunt
            keywords used to identify potential code blocks.
        TERRAFORM_PATTERNS (ClassVar[list[str]]): List of regex patterns used
            to match commented out Terraform/OpenTofu/Terragrunt syntax.
        root_path (Path): The root directory for relative path calculations.
        compiled_patterns (list[re.Pattern[str]]): Compiled regex patterns for
            efficient matching.

    """

    # Terraform, OpenTofu, and Terragrunt keywords that indicate code structure
    TERRAFORM_KEYWORDS: ClassVar[set[str]] = {
        # Common Terraform/OpenTofu keywords
        "resource",
        "data",
        "variable",
        "output",
        "locals",
        "module",
        "provider",
        "terraform",
        "backend",
        "required_providers",
        "required_version",
        "provisioner",
        "connection",
        "lifecycle",
        "depends_on",
        "count",
        "for_each",
        "dynamic",
        "content",
        # Terragrunt-specific keywords
        "include",
        "dependency",
        "dependencies",
        "inputs",
        "generate",
        "remote_state",
        "terraform_binary",
        "terragrunt_version_constraints",
        "download_dir",
        "iam_role",
        "prevent_destroy",
        "skip",
        "retryable_errors",
        "retry_max_attempts",
        "retry_sleep_interval_sec",
    }

    # Common argument patterns
    TERRAFORM_PATTERNS: ClassVar[list[str]] = [
        r"^\s*#\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=",  # variable assignment
        r"^\s*#\s*[a-zA-Z_][a-zA-Z0-9_]*\s*{",  # block opening
        r"^\s*#\s*}",  # block closing
        r'^\s*#\s*"[^"]*"\s*=',  # quoted key assignment
        r'^\s*#\s*"[^"]*"\s*{',  # quoted key block
        # Terragrunt-specific patterns
        r"^\s*#\s*source\s*=",  # terragrunt source
        r"^\s*#\s*config_path\s*=",  # terragrunt config path
        r"^\s*#\s*path\s*=",  # terragrunt include path
    ]

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize the detector with an optional root path.

        Args:
            root_path (Optional[Path]): The root directory to use for relative
                path calculations in results. If None, uses current working
                directory. This doesn't limit scanning scope, only affects
                how paths are displayed in results.

        Examples:
            >>> detector = TerraformCommentDetector()  # Uses current directory
            >>> detector = TerraformCommentDetector(Path("/my/project"))

        """
        self.root_path = root_path or Path.cwd()
        self.compiled_patterns = [re.compile(pattern) for pattern in self.TERRAFORM_PATTERNS]

    def find_terraform_files(self, directory: Path) -> Iterator[Path]:
        """Find all Terraform/OpenTofu/Terragrunt files in the given directory.

        Recursively searches for files with .tf, .tfvars, and .hcl extensions,
        excluding hidden files and directories. Supports Terraform, OpenTofu,
        and Terragrunt configuration files.

        Args:
            directory (Path): The directory to search for IaC files.

        Yields:
            Path: Each Terraform/OpenTofu/Terragrunt file found in the directory tree.

        Examples:
            >>> detector = TerraformCommentDetector()
            >>> files = list(detector.find_terraform_files(Path("./terraform")))
            >>> print(f"Found {len(files)} IaC files")
            >>> for file in files:
            ...     print(f"  {file}")

        Note:
            Skips files and directories starting with '.' (hidden files).
            Supports:
            - .tf files (Terraform/OpenTofu)
            - .tofu files (OpenTofu)
            - .tfvars files (Terraform/OpenTofu variables)
            - .hcl files (Terragrunt configurations)

        """
        terraform_extensions = {".tf", ".tofu", ".tfvars", ".hcl"}

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in terraform_extensions:
                # Skip hidden directories and files
                if any(part.startswith(".") for part in file_path.parts):
                    continue
                yield file_path

    def is_terraform_code_line(self, line: str) -> bool:
        r"""Check if a commented line looks like Terraform/OpenTofu/Terragrunt code.

        Analyzes a line to determine if it appears to be commented-out
        Terraform, OpenTofu, or Terragrunt configuration rather than
        a documentation comment.

        Args:
            line (str): The line of text to analyze.

        Returns:
            bool: True if the line appears to be commented IaC code,
                False if it's likely a documentation comment or not code.

        Examples:
            >>> detector = TerraformCommentDetector()
            >>> detector.is_terraform_code_line("# resource \"aws_instance\" \"web\" {")
            True
            >>> detector.is_terraform_code_line("# include {")
            True
            >>> detector.is_terraform_code_line("# This is a documentation comment")
            False
            >>> detector.is_terraform_code_line("# instance_type = \"t2.micro\"")
            True

        Note:
            Uses pattern matching and keyword detection to distinguish
            between code and comments. Supports Terraform, OpenTofu, and
            Terragrunt syntax. Skips TODO/FIXME/NOTE style comments.

        """
        stripped = line.strip()

        # Must start with # to be a comment
        if not stripped.startswith("#"):
            return False

        # Remove the # and any whitespace
        content = stripped[1:].strip()

        # Skip empty comments or documentation-style comments
        if not content:
            return False

        # Skip comments that look like documentation
        if content.startswith(("TODO", "FIXME", "NOTE", "HACK")):
            return False

        # Check for Terraform keywords
        first_word = content.split()[0] if content.split() else ""
        if first_word in self.TERRAFORM_KEYWORDS:
            return True

        # Check against patterns
        return any(pattern.match(stripped) for pattern in self.compiled_patterns)

    def _read_file_lines(self, file_path: Path) -> list[str]:
        """Read lines from a file, handling encoding errors gracefully.

        Args:
            file_path (Path): Path to the file to read.

        Returns:
            list[str]: List of lines from the file, empty list if file cannot be read.

        """
        try:
            with file_path.open(encoding="utf-8") as f:
                return f.readlines()
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return []

    def _finalize_current_block(
        self, file_path: Path, current_block_start: int, current_block_lines: list[str]
    ) -> CommentedCodeBlock:
        """Create a block from current accumulated lines.

        Args:
            file_path (Path): Path to the file containing the block.
            current_block_start (int): Starting line number of the block.
            current_block_lines (list[str]): Lines in the current block.

        Returns:
            CommentedCodeBlock: The created block.

        """
        return self._create_block(
            file_path,
            current_block_start,
            current_block_start + len(current_block_lines) - 1,
            current_block_lines,
        )

    def find_commented_blocks(self, file_path: Path) -> list[CommentedCodeBlock]:
        """Find all commented code blocks in a single file.

        Scans the file line by line to identify sequences of commented-out
        Terraform/OpenTofu/Terragrunt code. Uses intelligent block detection
        to handle blank commented lines within code blocks.

        Args:
            file_path (Path): Path to the file to scan.

        Returns:
            list[CommentedCodeBlock]: List of detected commented code blocks.
            Empty list if file cannot be read or contains no commented code.

        Examples:
            >>> detector = TerraformCommentDetector()
            >>> blocks = detector.find_commented_blocks(Path("main.tf"))
            >>> print(f"Found {len(blocks)} commented blocks")

        Note:
            Skips files that cannot be read due to encoding or IO errors.

        """
        lines = self._read_file_lines(file_path)
        if not lines:
            return []

        blocks: list[CommentedCodeBlock] = []
        current_block_lines: list[str] = []
        current_block_start = None

        for line_num, line in enumerate(lines, 1):
            if self.is_terraform_code_line(line):
                if current_block_start is None:
                    current_block_start = line_num
                current_block_lines.append(line)
            elif self._is_commented_blank_line(line) and current_block_start is not None:
                # Continue the current block for commented blank lines
                current_block_lines.append(line)
            elif self._is_block_continuation_line(line) and current_block_start is not None:
                # Continue the current block for special continuation cases (EOF, closing braces)
                current_block_lines.append(line)
            elif current_block_start is not None:
                # End the current block
                blocks.append(self._finalize_current_block(file_path, current_block_start, current_block_lines))
                current_block_start = None
                current_block_lines = []

        # Handle block at end of file
        if current_block_start is not None:
            blocks.append(self._finalize_current_block(file_path, current_block_start, current_block_lines))

        return blocks

    def _is_commented_blank_line(self, line: str) -> bool:
        """Check if a line is a commented blank line that should continue a block.

        Args:
            line (str): The line to check.

        Returns:
            bool: True if this is a commented blank line (# with only whitespace).

        """
        stripped = line.strip()
        # Check if it's a comment with only whitespace after the #
        return stripped.startswith("#") and stripped[1:].strip() == ""

    def _is_block_continuation_line(self, line: str) -> bool:
        """Check if a line should continue a block even if not detected as code.

        This handles special cases like EOF markers in heredoc syntax that are
        part of the code structure but don't match typical IaC patterns.

        Args:
            line (str): The line to check.

        Returns:
            bool: True if this line should continue the current block.

        """
        stripped = line.strip()

        # Must start with # to be a comment
        if not stripped.startswith("#"):
            return False

        # Remove the # and any whitespace
        content = stripped[1:].strip()

        # Special cases that should continue blocks
        special_continuations = {
            "EOF",  # Heredoc EOF markers
            "}",  # Closing braces (might be standalone)
        }

        return content in special_continuations

    def _create_block(self, file_path: Path, start_line: int, end_line: int, lines: list[str]) -> CommentedCodeBlock:
        """Create a CommentedCodeBlock from the given parameters."""
        relative_path = file_path.relative_to(self.root_path)
        first_line = lines[0].strip() if lines else ""
        full_content = "".join(lines)

        return CommentedCodeBlock(
            file_path=relative_path,
            line_number=start_line,
            end_line_number=end_line,
            first_line=first_line,
            full_content=full_content,
        )

    def scan_directory(self, directory: Optional[Path] = None) -> DetectionResult:
        """Scan a directory for commented out Terraform code.

        Recursively scans all .tf and .tfvars files in the specified directory
        (or root_path if none specified) to find commented-out code blocks.

        Args:
            directory (Optional[Path]): Directory to scan. If None, uses the
                root_path specified during initialization. Defaults to None.

        Returns:
            DetectionResult: Object containing all found commented blocks and
                scanning statistics including total files scanned and number
                of files containing commented code.

        Examples:
            >>> detector = TerraformCommentDetector()
            >>> result = detector.scan_directory(Path("./terraform"))
            >>> if result.has_commented_code:
            ...     print(f"Found {result.total_blocks} blocks in {result.files_with_comments} files")
            ...     for block in result.blocks:
            ...         print(f"  {block.relative_path}:{block.line_range}")

            >>> # Scan current directory
            >>> result = detector.scan_directory()
            >>> print(f"Scanned {result.total_files_scanned} files")

        Note:
            Returns empty result if directory doesn't exist. Logs progress
            at debug/info levels during scanning.

        """
        scan_path = directory or self.root_path

        if not scan_path.exists():
            logger.error(f"Directory does not exist: {scan_path}")
            return DetectionResult(blocks=[], total_files_scanned=0, files_with_comments=0)

        all_blocks: list[CommentedCodeBlock] = []
        total_files = files_with_comments = 0

        for tf_file in self.find_terraform_files(scan_path):
            total_files += 1
            logger.debug(f"Scanning file: {tf_file}")

            blocks = self.find_commented_blocks(tf_file)
            if blocks:
                files_with_comments += 1
                all_blocks.extend(blocks)
                logger.info(f"Found {len(blocks)} commented block(s) in {tf_file}")

        logger.info(f"Scanned {total_files} Terraform files, found commented code in {files_with_comments} files")

        return DetectionResult(
            blocks=all_blocks, total_files_scanned=total_files, files_with_comments=files_with_comments
        )

    def fix_commented_blocks(self, blocks: list[CommentedCodeBlock]) -> int:
        """Remove commented code blocks from their respective files.

        Args:
            blocks: list of commented code blocks to remove

        Returns:
            Number of blocks successfully removed

        """
        if not blocks:
            return 0

        # Group blocks by file
        blocks_by_file: dict[Path, list[CommentedCodeBlock]] = {}
        for block in blocks:
            full_path = self.root_path / block.file_path
            if full_path not in blocks_by_file:
                blocks_by_file[full_path] = []
            blocks_by_file[full_path].append(block)

        fixed_count = 0

        for file_path, file_blocks in blocks_by_file.items():
            try:
                # Read the original file
                with file_path.open(encoding="utf-8") as f:
                    lines = f.readlines()

                # Sort blocks by line number in reverse order to avoid index shifting
                file_blocks.sort(key=lambda b: b.line_number, reverse=True)

                # Remove the commented blocks
                for block in file_blocks:
                    # Convert to 0-based indexing
                    start_idx = block.line_number - 1
                    end_idx = block.end_line_number

                    # Remove the lines
                    del lines[start_idx:end_idx]
                    fixed_count += 1

                    logger.info(f"Removed commented block from {file_path}:{block.line_number}-{block.end_line_number}")

                # Write the modified file back
                with file_path.open("w", encoding="utf-8") as f:
                    f.writelines(lines)

            except (OSError, UnicodeDecodeError) as e:
                logger.error(f"Could not fix file {file_path}: {e}")
                continue

        return fixed_count
