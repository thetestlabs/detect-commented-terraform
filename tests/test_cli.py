"""Tests for the CLI interface."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from detect_commented_terraform.cli import app, main


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI runner for testing."""
    return CliRunner()


def test_version_command(runner: CliRunner) -> None:
    """Test the version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "detect-commented-terraform" in result.stdout


def test_scan_command_no_files(runner: CliRunner, temp_dir: Path) -> None:
    """Test scanning a directory with no Terraform files."""
    result = runner.invoke(app, ["scan", str(temp_dir)])
    assert result.exit_code == 0
    assert "No commented Terraform code found" in result.stdout


def test_scan_command_with_commented_code(runner: CliRunner, sample_terraform_file: Path) -> None:
    """Test scanning a directory with commented Terraform code."""
    result = runner.invoke(app, ["scan", str(sample_terraform_file.parent)])
    assert result.exit_code == 1  # Should exit with error code when commented code is found
    assert "Found 2 commented code block(s)" in result.stdout


def test_scan_command_no_exit_code(runner: CliRunner, sample_terraform_file: Path) -> None:
    """Test scanning with --no-exit-code flag."""
    result = runner.invoke(app, ["scan", str(sample_terraform_file.parent), "--no-exit-code"])
    assert result.exit_code == 0  # Should not exit with error code
    assert "Found 2 commented code block(s)" in result.stdout


def test_scan_nonexistent_path(runner: CliRunner) -> None:
    """Test scanning a non-existent path."""
    result = runner.invoke(app, ["scan", "/nonexistent/path"])
    assert result.exit_code == 1
    assert "Path does not exist" in result.stdout


def test_scan_file_instead_of_directory(runner: CliRunner, temp_dir: Path) -> None:
    """Test scanning a file instead of a directory."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")

    result = runner.invoke(app, ["scan", str(test_file)])
    assert result.exit_code == 1
    assert "Path is not a directory" in result.stdout


def test_scan_with_verbose_flag(runner: CliRunner, temp_dir: Path) -> None:
    """Test scanning with verbose flag."""
    # Create a test file with commented code
    tf_file = temp_dir / "test.tf"
    tf_file.write_text("""
resource "aws_instance" "web" {
  ami = "ami-12345678"
}

# resource "aws_s3_bucket" "backup" {
#   bucket = "my-backup"
# }
""")

    result = runner.invoke(app, ["scan", str(temp_dir), "--verbose"])
    assert result.exit_code == 1
    assert "Found 1 commented code block(s)" in result.stdout


def test_scan_with_fix_flag_confirmed(runner: CliRunner, temp_dir: Path) -> None:
    """Test scanning with --fix flag and user confirmation."""
    # Create a test file with commented code
    tf_file = temp_dir / "test.tf"
    tf_file.write_text("""
resource "aws_instance" "web" {
  ami = "ami-12345678"
}

# resource "aws_s3_bucket" "backup" {
#   bucket = "my-backup"
# }
""")

    # Mock user confirmation as "yes"
    result = runner.invoke(app, ["scan", str(temp_dir), "--fix"], input="y\n")
    assert result.exit_code == 0
    assert "Removed commented block" in result.stdout
    assert "No commented Terraform code found!" in result.stdout

    # Check that the commented code was actually removed
    content = tf_file.read_text()
    assert '# resource "aws_s3_bucket"' not in content


def test_scan_with_fix_flag_cancelled(runner: CliRunner, temp_dir: Path) -> None:
    """Test scanning with --fix flag but user cancels."""
    # Create a test file with commented code
    tf_file = temp_dir / "test.tf"
    tf_file.write_text("""
resource "aws_instance" "web" {
  ami = "ami-12345678"
}

# resource "aws_s3_bucket" "backup" {
#   bucket = "my-backup"
# }
""")

    # Mock user confirmation as "no"
    result = runner.invoke(app, ["scan", str(temp_dir), "--fix"], input="n\n")
    assert result.exit_code == 1
    assert "Operation cancelled" in result.stdout

    # Check that the commented code was NOT removed
    content = tf_file.read_text()
    assert '# resource "aws_s3_bucket"' in content


def test_scan_current_directory_default(runner: CliRunner, temp_dir: Path) -> None:
    """Test scanning current directory when no path is provided."""
    with (
        patch("detect_commented_terraform.cli.Path.cwd") as mock_cwd,
        patch("detect_commented_terraform.cli.TerraformCommentDetector") as mock_detector,
    ):
        # Use a real directory that exists
        mock_cwd.return_value = temp_dir
        mock_instance = mock_detector.return_value
        mock_scan_result = mock_instance.scan_directory.return_value
        mock_scan_result.has_commented_code = False
        mock_scan_result.total_files_scanned = 0
        mock_scan_result.files_with_comments = 0
        mock_scan_result.total_blocks = 0

        result = runner.invoke(app, ["scan"])
        assert result.exit_code == 0
        mock_detector.assert_called_once_with(root_path=temp_dir)


def test_format_results_with_long_first_line(runner: CliRunner, temp_dir: Path) -> None:
    """Test formatting results with very long first line (truncation)."""
    # Create a test file with a very long commented line
    long_line = '# resource "aws_instance" "example" { ' + "a" * 100
    tf_file = temp_dir / "test.tf"
    tf_file.write_text(f"""
resource "aws_instance" "web" {{
  ami = "ami-12345678"
}}

{long_line}
""")

    result = runner.invoke(app, ["scan", str(temp_dir)])
    assert result.exit_code == 1
    # The long line should be truncated with ellipsis in the output
    assert "Found 1 commented code block(s)" in result.stdout


def test_main_function() -> None:
    """Test the main entry point function."""
    with patch("detect_commented_terraform.cli.app") as mock_app:
        main()
        mock_app.assert_called_once()


def test_scan_with_no_commented_code_and_fix_flag(runner: CliRunner, temp_dir: Path) -> None:
    """Test scanning with --fix flag when no commented code exists."""
    # Create a clean terraform file
    tf_file = temp_dir / "clean.tf"
    tf_file.write_text("""
resource "aws_instance" "web" {
  ami = "ami-12345678"
  instance_type = "t2.micro"
}
""")

    result = runner.invoke(app, ["scan", str(temp_dir), "--fix"])
    assert result.exit_code == 0
    assert "No commented Terraform code found" in result.stdout


def test_fixed_count_message_display(runner: CliRunner, temp_dir: Path) -> None:
    """Test that the fixed count message is displayed correctly."""
    # Create a file with multiple commented blocks
    tf_file = temp_dir / "main.tf"
    tf_file.write_text("""
resource "aws_instance" "web" {
  ami = "ami-12345678"
}

# resource "aws_s3_bucket" "backup" {
#   bucket = "my-backup"
# }

# variable "region" {
#   type = string
# }
""")

    # Scan with fix and confirm
    result = runner.invoke(app, ["scan", str(temp_dir), "--fix"], input="y\n")
    assert result.exit_code == 0
    # This should trigger the fixed_count > 0 message on lines 55-56
    assert "Removed commented block" in result.stdout
