"""Data models for the detect-commented-terraform package."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CommentedCodeBlock:
    r"""Represents a block of commented out Terraform code.

    A data structure that holds information about a contiguous block
    of commented-out Terraform configuration found in a file.

    Attributes:
        file_path (Path): Path to the file containing the commented block.
            This is typically a relative path from the scan root.
        line_number (int): Starting line number of the block (1-indexed).
        end_line_number (int): Ending line number of the block (1-indexed).
        first_line (str): The first line of the commented block, used for
            display purposes and quick identification.
        full_content (str): Complete text content of the entire block,
            including all comment symbols and whitespace.

    Examples:
        >>> block = CommentedCodeBlock(
        ...     file_path=Path("main.tf"),
        ...     line_number=15,
        ...     end_line_number=18,
        ...     first_line='# resource "aws_instance" "web" {',
        ...     full_content='# resource "aws_instance" "web" {\\n#   ami = "..."\\n# }'
        ... )
        >>> print(f"Found block at {block.line_range}")
        Found block at 15-18
        >>> print(block.relative_path)
        main.tf

    """

    file_path: Path
    line_number: int
    end_line_number: int
    first_line: str
    full_content: str

    @property
    def relative_path(self) -> str:
        """Get the relative path as a string.

        Returns:
            str: String representation of the file path.

        Examples:
            >>> block.relative_path
            'terraform/main.tf'

        """
        return str(self.file_path)

    @property
    def line_range(self) -> str:
        """Get the line range as a string.

        Returns:
            str: Line range formatted as either single line number or
                range "start-end" for multi-line blocks.

        Examples:
            >>> block.line_range  # Single line
            '42'
            >>> block.line_range  # Multi-line
            '15-18'

        """
        if self.line_number == self.end_line_number:
            return str(self.line_number)
        return f"{self.line_number}-{self.end_line_number}"

    def __str__(self) -> str:
        """Return string representation of the commented code block.

        Returns:
            str: Formatted string showing file path, line range, and first line.

        Examples:
            >>> str(block)
            'main.tf:15-18 - resource "aws_instance" "web" {'

        """
        return f"{self.relative_path}:{self.line_range} - {self.first_line.strip()}"


@dataclass
class DetectionResult:
    """Result of scanning for commented Terraform code.

    Contains the results of scanning one or more Terraform files for
    commented-out code blocks, including all found blocks and statistics.

    Attributes:
        blocks (list[CommentedCodeBlock]): All commented code blocks found
            during the scan, ordered by file path and line number.
        total_files_scanned (int): Total number of files that were scanned.
        files_with_comments (int): Number of files that contained at least
            one commented code block.

    Examples:
        >>> result = DetectionResult(
        ...     blocks=[block1, block2],
        ...     total_files_scanned=5,
        ...     files_with_comments=2
        ... )
        >>> if result.has_commented_code:
        ...     print(f"Found {result.total_blocks} blocks")
        Found 2 blocks
        >>> print(f"Scanned {result.total_files_scanned} files")
        Scanned 5 files

    """

    blocks: list[CommentedCodeBlock]
    total_files_scanned: int
    files_with_comments: int

    @property
    def has_commented_code(self) -> bool:
        """Check if any commented code was found.

        Returns:
            bool: True if one or more commented code blocks were found,
                False if no blocks were detected.

        Examples:
            >>> result.has_commented_code
            True
            >>> empty_result.has_commented_code
            False

        """
        return len(self.blocks) > 0

    @property
    def total_blocks(self) -> int:
        """Get the total number of commented code blocks.

        Returns:
            int: Total count of commented code blocks found across all files.

        Examples:
            >>> result.total_blocks
            5

        """
        return len(self.blocks)
