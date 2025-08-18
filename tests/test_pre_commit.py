"""Tests for pre-commit hook functionality."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from detect_commented_terraform.detector import TerraformCommentDetector
from detect_commented_terraform.pre_commit import main, run_pre_commit_hook


def test_run_pre_commit_hook_no_files() -> None:
    """Test pre-commit hook with no files."""
    result = run_pre_commit_hook([])
    assert result == 0


def test_run_pre_commit_hook_no_terraform_files() -> None:
    """Test pre-commit hook with no Terraform files."""
    result = run_pre_commit_hook(["README.md", "setup.py", "requirements.txt"])
    assert result == 0


def test_run_pre_commit_hook_clean_terraform_files(temp_dir: Path) -> None:
    """Test pre-commit hook with clean Terraform files."""
    # Create clean Terraform files
    main_tf = temp_dir / "main.tf"
    main_tf.write_text("""
# This is a documentation comment
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  tags = {
    Name = "HelloWorld"
  }
}
""")

    variables_tf = temp_dir / "variables.tf"
    variables_tf.write_text("""
# Variable definitions
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}
""")

    result = run_pre_commit_hook([str(main_tf), str(variables_tf)], root_path=temp_dir)
    assert result == 0


def test_run_pre_commit_hook_with_commented_code(temp_dir: Path, capsys: Any) -> None:
    """Test pre-commit hook with commented Terraform code."""
    # Create Terraform file with commented code
    main_tf = temp_dir / "main.tf"
    main_tf.write_text("""
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}

# resource "aws_s3_bucket" "backup" {
#   bucket = "my-backup-bucket"
#   versioning {
#     enabled = true
#   }
# }

# data "aws_ami" "ubuntu" {
#   most_recent = true
# }
""")

    # Resolve paths to handle symlinks on macOS
    resolved_tf = main_tf.resolve()
    resolved_temp_dir = temp_dir.resolve()

    result = run_pre_commit_hook([str(resolved_tf)], root_path=resolved_temp_dir)

    # Should return 1 (failure) when commented code is found
    assert result == 1

    # Check output contains information about found blocks
    captured = capsys.readouterr()
    assert "❌ Found" in captured.out
    assert "commented Terraform code block(s)" in captured.out


def test_run_pre_commit_hook_mixed_files(temp_dir: Path, capsys: Any) -> None:
    """Test pre-commit hook with mix of clean and problematic files."""
    # Clean file
    clean_tf = temp_dir / "clean.tf"
    clean_tf.write_text("""
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
""")

    # File with commented code
    problematic_tf = temp_dir / "problematic.tf"
    problematic_tf.write_text("""
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}

# resource "aws_s3_bucket" "backup" {
#   bucket = "my-backup-bucket"
# }
""")

    # Non-Terraform file (should be ignored)
    readme = temp_dir / "README.md"
    readme.write_text("# README")

    # Resolve paths to handle symlinks on macOS
    resolved_clean = clean_tf.resolve()
    resolved_problematic = problematic_tf.resolve()
    resolved_readme = readme.resolve()
    resolved_temp_dir = temp_dir.resolve()

    result = run_pre_commit_hook(
        [str(resolved_clean), str(resolved_problematic), str(resolved_readme)], root_path=resolved_temp_dir
    )

    # Should return 1 because problematic.tf has commented code
    assert result == 1

    captured = capsys.readouterr()
    assert "❌ Found" in captured.out


def test_run_pre_commit_hook_nonexistent_files() -> None:
    """Test pre-commit hook with nonexistent Terraform files."""
    nonexistent_tf = "/path/to/nonexistent.tf"
    result = run_pre_commit_hook([nonexistent_tf])
    assert result == 0


def test_run_pre_commit_hook_with_root_path(temp_dir: Path) -> None:
    """Test pre-commit hook with explicit root path."""
    # Create a Terraform file with commented code
    tf_file = temp_dir / "test.tf"
    tf_file.write_text("""
# resource "aws_instance" "test" {
#   ami = "ami-12345"
# }
""")

    # Resolve paths to handle symlinks on macOS
    resolved_tf = tf_file.resolve()
    resolved_temp_dir = temp_dir.resolve()

    result = run_pre_commit_hook([str(resolved_tf)], root_path=resolved_temp_dir)
    assert result == 1


def test_run_pre_commit_hook_relative_paths(temp_dir: Path, monkeypatch: Any) -> None:
    """Test pre-commit hook with relative file paths."""
    # Change to temp directory
    monkeypatch.chdir(temp_dir)

    # Create Terraform file with relative path
    tf_file = temp_dir / "main.tf"
    tf_file.write_text("""
resource "aws_instance" "web" {
  ami = "ami-12345678"
}
""")

    # Use relative path
    result = run_pre_commit_hook(["main.tf"])
    assert result == 0


def test_run_pre_commit_hook_multiple_blocks(temp_dir: Path, capsys: Any) -> None:
    """Test pre-commit hook with multiple commented blocks."""
    tf_file = temp_dir / "multiple.tf"
    tf_file.write_text("""
resource "aws_instance" "web" {
  ami = "ami-12345678"
}

# resource "aws_s3_bucket" "first" {
#   bucket = "first-bucket"
# }

# Some documentation comment
# This explains the next resource

# resource "aws_s3_bucket" "second" {
#   bucket = "second-bucket"
#   versioning {
#     enabled = true
#   }
# }

# data "aws_availability_zones" "available" {
#   state = "available"
# }
""")

    # Resolve paths to handle symlinks on macOS
    resolved_tf = tf_file.resolve()
    resolved_temp_dir = temp_dir.resolve()

    result = run_pre_commit_hook([str(resolved_tf)], root_path=resolved_temp_dir)
    assert result == 1

    captured = capsys.readouterr()
    # Should find multiple blocks
    assert "❌ Found" in captured.out
    assert "commented Terraform code block(s)" in captured.out


@patch("sys.argv", ["pre_commit.py", "test.tf"])
@patch("detect_commented_terraform.pre_commit.run_pre_commit_hook")
def test_main_entry_point(mock_run_hook: MagicMock) -> None:
    """Test the main entry point function."""
    mock_run_hook.return_value = 0

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    mock_run_hook.assert_called_once_with(["test.tf"])


@patch("sys.argv", ["pre_commit.py", "file1.tf", "file2.tf"])
@patch("detect_commented_terraform.pre_commit.run_pre_commit_hook")
def test_main_with_multiple_files(mock_run_hook: MagicMock) -> None:
    """Test main with multiple files."""
    mock_run_hook.return_value = 1

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    mock_run_hook.assert_called_once_with(["file1.tf", "file2.tf"])


@patch("sys.argv", ["pre_commit.py"])
@patch("detect_commented_terraform.pre_commit.run_pre_commit_hook")
def test_main_no_files(mock_run_hook: MagicMock) -> None:
    """Test main with no files."""
    mock_run_hook.return_value = 0

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    mock_run_hook.assert_called_once_with([])


def test_pre_commit_hook_output_format(temp_dir: Path, capsys: Any) -> None:
    """Test that pre-commit hook output format is user-friendly."""
    tf_file = temp_dir / "test.tf"
    tf_file.write_text("""
# resource "aws_instance" "test" {
#   ami = "ami-12345"
# }
""")

    # Resolve paths to handle symlinks on macOS
    resolved_tf = tf_file.resolve()
    resolved_temp_dir = temp_dir.resolve()

    result = run_pre_commit_hook([str(resolved_tf)], root_path=resolved_temp_dir)
    assert result == 1

    captured = capsys.readouterr()
    output_lines = captured.out.strip().split("\n")

    # Check output format
    assert len(output_lines) >= 2  # Header + at least one block
    assert output_lines[0].startswith("❌ Found")
    assert "commented Terraform code block(s)" in output_lines[0]
    # Each subsequent line should show a block
    for line in output_lines[1:]:
        assert line.startswith("  ")  # Indented


def test_pre_commit_hook_with_tfvars_files(temp_dir: Path) -> None:
    """Test pre-commit hook with .tfvars files."""
    # Clean tfvars file
    clean_tfvars = temp_dir / "terraform.tfvars"
    clean_tfvars.write_text("""
region = "us-west-2"
instance_type = "t2.micro"
""")

    # Problematic tfvars file
    problematic_tfvars = temp_dir / "problematic.tfvars"
    problematic_tfvars.write_text("""
region = "us-west-2"
# instance_type = "t2.large"
""")

    # Resolve paths to handle symlinks on macOS
    resolved_clean = clean_tfvars.resolve()
    resolved_problematic = problematic_tfvars.resolve()
    resolved_temp_dir = temp_dir.resolve()

    # Test clean file
    result = run_pre_commit_hook([str(resolved_clean)], root_path=resolved_temp_dir)
    assert result == 0

    # Test problematic file
    result = run_pre_commit_hook([str(resolved_problematic)], root_path=resolved_temp_dir)
    assert result == 1


def test_pre_commit_hook_error_handling(temp_dir: Path, monkeypatch: Any) -> None:
    """Test pre-commit hook handles errors gracefully."""
    # Create a file that exists initially
    tf_file = temp_dir / "test.tf"
    tf_file.write_text('resource "aws_instance" "test" {}')

    # Mock file operations to simulate an error
    def mock_find_commented_blocks(self: Any, file_path: Any) -> Any:
        raise PermissionError("Permission denied")

    # Patch the method
    monkeypatch.setattr(TerraformCommentDetector, "find_commented_blocks", mock_find_commented_blocks)

    # Resolve paths to handle symlinks on macOS
    resolved_tf = tf_file.resolve()
    resolved_temp_dir = temp_dir.resolve()

    # Should handle the error and return 0 (no blocks found due to error)
    result = run_pre_commit_hook([str(resolved_tf)], root_path=resolved_temp_dir)
    assert result == 0


def test_pre_commit_hook_empty_terraform_file(temp_dir: Path) -> None:
    """Test pre-commit hook with empty Terraform files."""
    empty_tf = temp_dir / "empty.tf"
    empty_tf.write_text("")

    result = run_pre_commit_hook([str(empty_tf)], root_path=temp_dir)
    assert result == 0


def test_pre_commit_hook_only_comments(temp_dir: Path) -> None:
    """Test pre-commit hook with file containing only documentation comments."""
    comments_tf = temp_dir / "comments.tf"
    comments_tf.write_text("""
# This file contains infrastructure definitions
# TODO: Add S3 bucket configuration
# NOTE: Remember to update the AMI ID
""")

    result = run_pre_commit_hook([str(comments_tf)], root_path=temp_dir)
    assert result == 0
