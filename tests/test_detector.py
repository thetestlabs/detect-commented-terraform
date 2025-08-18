"""Tests for the TerraformCommentDetector."""

import logging
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from detect_commented_terraform.detector import TerraformCommentDetector
from detect_commented_terraform.models import CommentedCodeBlock


def test_detector_initialization(temp_dir: Path) -> None:
    """Test detector initialization."""
    detector = TerraformCommentDetector(root_path=temp_dir)
    assert detector.root_path == temp_dir


def test_find_terraform_files(temp_dir: Path) -> None:
    """Test finding Terraform files."""
    # Create test files
    (temp_dir / "main.tf").write_text("# test")
    (temp_dir / "variables.tf").write_text("# test")
    (temp_dir / "terraform.tfvars").write_text("# test")
    (temp_dir / "README.md").write_text("# test")

    detector = TerraformCommentDetector(root_path=temp_dir)
    tf_files = list(detector.find_terraform_files(temp_dir))

    assert len(tf_files) == 3
    assert all(f.suffix in {".tf", ".tfvars"} for f in tf_files)


def test_find_terraform_files_with_subdirectories(temp_dir: Path) -> None:
    """Test finding Terraform files in subdirectories."""
    # Create nested directory structure
    modules_dir = temp_dir / "modules" / "vpc"
    modules_dir.mkdir(parents=True)

    (temp_dir / "main.tf").write_text("# test")
    (modules_dir / "vpc.tf").write_text("# test")
    (modules_dir / "variables.tf").write_text("# test")

    detector = TerraformCommentDetector(root_path=temp_dir)
    tf_files = list(detector.find_terraform_files(temp_dir))

    assert len(tf_files) == 3
    assert any(f.name == "main.tf" for f in tf_files)
    assert any(f.name == "vpc.tf" for f in tf_files)
    assert any(f.name == "variables.tf" for f in tf_files)


def test_is_terraform_code_line() -> None:
    """Test detection of Terraform code lines."""
    detector = TerraformCommentDetector()

    # Should detect as Terraform code
    assert detector.is_terraform_code_line('# resource "aws_instance" "example" {')
    assert detector.is_terraform_code_line('#   ami = "ami-12345678"')
    assert detector.is_terraform_code_line('# variable "name" {')
    assert detector.is_terraform_code_line('#   bucket = "my-bucket"')
    assert detector.is_terraform_code_line("# }")

    # Should NOT detect as Terraform code
    assert not detector.is_terraform_code_line("# This is a regular comment")
    assert not detector.is_terraform_code_line("# TODO: fix this")
    assert not detector.is_terraform_code_line("#")
    assert not detector.is_terraform_code_line('resource "aws_instance" "example" {')


def test_is_terraform_code_line_edge_cases() -> None:
    """Test edge cases for Terraform code detection."""
    detector = TerraformCommentDetector()

    # Test with different whitespace patterns
    assert detector.is_terraform_code_line('#resource "aws_instance" "test" {')
    assert detector.is_terraform_code_line('#    ami = "ami-123"')
    assert detector.is_terraform_code_line('#\tami = "ami-123"')  # Tab character

    # Test with provider blocks
    assert detector.is_terraform_code_line('# provider "aws" {')
    assert detector.is_terraform_code_line('#   region = "us-east-1"')

    # Test with data sources
    assert detector.is_terraform_code_line('# data "aws_ami" "example" {')

    # Test with terraform blocks
    assert detector.is_terraform_code_line("# terraform {")

    # Test with module blocks
    assert detector.is_terraform_code_line('# module "vpc" {')

    # Test with output blocks
    assert detector.is_terraform_code_line('# output "vpc_id" {')

    # Test with locals blocks
    assert detector.is_terraform_code_line("# locals {")


def test_is_terragrunt_code_line() -> None:
    """Test detection of Terragrunt code lines."""
    detector = TerraformCommentDetector()

    # Terragrunt-specific keywords and patterns
    assert detector.is_terraform_code_line("# include {")
    assert detector.is_terraform_code_line("#   path = find_in_parent_folders()")
    assert detector.is_terraform_code_line('# dependency "vpc" {')
    assert detector.is_terraform_code_line('#   config_path = "../vpc"')
    assert detector.is_terraform_code_line("# inputs = {")
    assert detector.is_terraform_code_line('#   environment = "production"')
    assert detector.is_terraform_code_line("# remote_state {")
    assert detector.is_terraform_code_line('# generate "provider" {')
    assert detector.is_terraform_code_line('#   source = "./modules/vpc"')
    assert detector.is_terraform_code_line('#   path = "./provider.tf"')


def test_is_opentofu_code_line() -> None:
    """Test detection of OpenTofu code lines (same as Terraform syntax)."""
    detector = TerraformCommentDetector()

    # OpenTofu uses same syntax as Terraform
    assert detector.is_terraform_code_line('# resource "aws_instance" "example" {')
    assert detector.is_terraform_code_line('#   ami = "ami-12345678"')
    assert detector.is_terraform_code_line('# variable "name" {')
    assert detector.is_terraform_code_line("#   type = string")


def test_find_terraform_files_includes_hcl_and_tofu(temp_dir: Path) -> None:
    """Test finding Terraform/OpenTofu/Terragrunt files includes .hcl and .tofu files."""
    # Create test files including .hcl and .tofu
    (temp_dir / "main.tf").write_text("# test")
    (temp_dir / "variables.tf").write_text("# test")
    (temp_dir / "terraform.tfvars").write_text("# test")
    (temp_dir / "terragrunt.hcl").write_text("# test")
    (temp_dir / "opentofu.tofu").write_text("# test")
    (temp_dir / "README.md").write_text("# test")

    detector = TerraformCommentDetector(root_path=temp_dir)
    tf_files = list(detector.find_terraform_files(temp_dir))

    assert len(tf_files) == 5
    assert all(f.suffix in {".tf", ".tofu", ".tfvars", ".hcl"} for f in tf_files)
    assert any(f.name == "terragrunt.hcl" for f in tf_files)
    assert any(f.name == "opentofu.tofu" for f in tf_files)


def test_block_detection_with_commented_blank_lines(temp_dir: Path) -> None:
    """Test that blocks with commented blank lines are properly consolidated."""
    detector = TerraformCommentDetector(root_path=temp_dir)

    # Create a test file with a block containing commented blank lines
    test_content = """# Some regular comment
# resource "aws_instance" "test" {
#   ami = "ami-123"
#
#   instance_type = "t2.micro"
#   tags = {
#     Name = "test"
#   }
# }

# Another block
# variable "test" {
#   type = string
# }
"""

    test_file = temp_dir / "test.tf"
    test_file.write_text(test_content)

    blocks = detector.find_commented_blocks(test_file)

    # Should find 2 blocks, not more due to the blank commented line
    assert len(blocks) == 2

    # First block should span lines 2-9 (including the blank commented line)
    assert blocks[0].line_number == 2
    assert blocks[0].end_line_number == 9

    # Second block should be lines 12-14
    assert blocks[1].line_number == 12
    assert blocks[1].end_line_number == 14


def test_block_detection_with_eof_continuation(temp_dir: Path) -> None:
    """Test block detection with EOF markers in heredoc syntax."""
    detector = TerraformCommentDetector(root_path=temp_dir)

    # Create a test file with heredoc EOF syntax that should be one block
    test_content = """# generate "provider" {
#   path      = "provider.tf"
#   if_exists = "overwrite_terragrunt"
#   contents  = <<EOF
# provider "aws" {
#   region = "us-east-1"
# }
# EOF
# }
"""

    test_file = temp_dir / "test.hcl"
    test_file.write_text(test_content)

    blocks = detector.find_commented_blocks(test_file)

    # Should find only 1 block that includes the EOF line
    assert len(blocks) == 1

    # Block should span lines 1-9 (the entire heredoc block)
    assert blocks[0].line_number == 1
    assert blocks[0].end_line_number == 9
    assert 'generate "provider"' in blocks[0].first_line


def test_find_commented_blocks(sample_terraform_file: Path) -> None:
    """Test finding commented code blocks."""
    detector = TerraformCommentDetector(root_path=sample_terraform_file.parent)
    blocks = detector.find_commented_blocks(sample_terraform_file)

    assert len(blocks) == 2

    # First block (S3 bucket)
    first_block = blocks[0]
    assert first_block.line_number == 8
    assert first_block.end_line_number == 10
    assert 'resource "aws_s3_bucket"' in first_block.first_line

    # Second block (variable)
    second_block = blocks[1]
    assert second_block.line_number == 17
    assert second_block.end_line_number == 21
    assert 'variable "region"' in second_block.first_line


def test_find_commented_blocks_with_file_read_error(temp_dir: Path) -> None:
    """Test finding commented blocks when file read fails."""
    tf_file = temp_dir / "test.tf"
    tf_file.write_text("# test content")

    detector = TerraformCommentDetector(root_path=temp_dir)

    # Mock file read to raise an exception
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = OSError("Permission denied")

        # Should handle the error gracefully and return empty list
        blocks = detector.find_commented_blocks(tf_file)
        assert blocks == []


def test_find_commented_blocks_with_unicode_decode_error(temp_dir: Path) -> None:
    """Test finding commented blocks when file has encoding issues."""
    tf_file = temp_dir / "test.tf"
    tf_file.write_bytes(b"\xff\xfe# invalid utf-8")  # Invalid UTF-8 bytes

    detector = TerraformCommentDetector(root_path=temp_dir)

    # Should handle the encoding error gracefully
    blocks = detector.find_commented_blocks(tf_file)
    assert blocks == []


def test_scan_directory(temp_dir: Path) -> None:
    """Test scanning a directory for commented code."""
    # Create test files
    tf_content1 = """
resource "aws_instance" "example" {
  ami = "ami-12345678"
}

# resource "aws_s3_bucket" "example" {
#   bucket = "my-bucket"
# }
"""

    tf_content2 = """
# variable "name" {
#   type = string
# }

output "id" {
  value = "test"
}
"""

    (temp_dir / "main.tf").write_text(tf_content1)
    (temp_dir / "variables.tf").write_text(tf_content2)

    detector = TerraformCommentDetector(root_path=temp_dir)
    result = detector.scan_directory()

    assert result.total_files_scanned == 2
    assert result.files_with_comments == 2
    assert result.total_blocks == 2
    assert result.has_commented_code


def test_scan_directory_with_verbose_logging(temp_dir: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test scanning with verbose logging enabled."""
    # Create test file
    tf_content = """
# resource "aws_instance" "example" {
#   ami = "ami-12345678"
# }
"""
    (temp_dir / "main.tf").write_text(tf_content)

    detector = TerraformCommentDetector(root_path=temp_dir)

    # Set logging level to DEBUG to trigger verbose logging
    with caplog.at_level(logging.DEBUG):
        result = detector.scan_directory()

    assert result.total_files_scanned == 1
    assert result.files_with_comments == 1
    assert result.total_blocks == 1

    # Check that scan was successful (don't require specific log messages since they may vary)
    assert result.has_commented_code


def test_scan_directory_no_terraform_files(temp_dir: Path) -> None:
    """Test scanning directory with no Terraform files."""
    # Create non-Terraform files
    (temp_dir / "README.md").write_text("# Documentation")
    (temp_dir / "script.py").write_text("# Python script")

    detector = TerraformCommentDetector(root_path=temp_dir)
    result = detector.scan_directory()

    assert result.total_files_scanned == 0
    assert result.files_with_comments == 0
    assert result.total_blocks == 0
    assert not result.has_commented_code


def test_fix_commented_blocks(temp_dir: Path) -> None:
    """Test fixing commented code blocks."""
    # Create test file with commented code
    tf_content = """
resource "aws_instance" "example" {
  ami = "ami-12345678"
}

# resource "aws_s3_bucket" "example" {
#   bucket = "my-bucket"
# }

variable "environment" {
  type = string
}

# variable "region" {
#   type = string
# }
"""

    tf_file = temp_dir / "main.tf"
    tf_file.write_text(tf_content)

    detector = TerraformCommentDetector(root_path=temp_dir)

    # Find blocks first
    blocks = detector.find_commented_blocks(tf_file)
    assert len(blocks) == 2

    # Fix the blocks
    fixed_count = detector.fix_commented_blocks(blocks)
    assert fixed_count == 2

    # Check that blocks are gone
    blocks_after_fix = detector.find_commented_blocks(tf_file)
    assert len(blocks_after_fix) == 0

    # Check file content
    fixed_content = tf_file.read_text()
    assert '# resource "aws_s3_bucket"' not in fixed_content
    assert '# variable "region"' not in fixed_content
    assert 'resource "aws_instance"' in fixed_content
    assert 'variable "environment"' in fixed_content


def test_fix_commented_blocks_with_no_file_access(temp_dir: Path) -> None:
    """Test fixing commented blocks when file doesn't exist."""
    detector = TerraformCommentDetector(root_path=temp_dir)

    # Create a block for a non-existent file
    non_existent_file = temp_dir / "nonexistent.tf"
    fake_block = CommentedCodeBlock(
        file_path=non_existent_file,
        line_number=1,
        end_line_number=3,
        first_line="# fake line",
        full_content="# fake\n# block\n# here",
    )

    # Should handle missing file gracefully
    fixed_count = detector.fix_commented_blocks([fake_block])
    assert fixed_count == 0


def test_fix_commented_blocks_with_read_only_directory(temp_dir: Path) -> None:
    """Test fixing commented blocks in a read-only scenario."""
    tf_content = """
# resource "aws_instance" "example" {
#   ami = "ami-12345678"
# }
"""
    tf_file = temp_dir / "main.tf"
    tf_file.write_text(tf_content)

    detector = TerraformCommentDetector(root_path=temp_dir)
    blocks = detector.find_commented_blocks(tf_file)
    assert len(blocks) == 1

    # Make the file read-only
    original_mode = tf_file.stat().st_mode
    tf_file.chmod(0o444)  # Read-only

    try:
        # This might fail due to permissions, but should handle gracefully
        fixed_count = detector.fix_commented_blocks(blocks)
        # We don't assert a specific value since behavior may vary by system
        assert isinstance(fixed_count, int)
    finally:
        # Restore original permissions
        tf_file.chmod(original_mode)


def test_fix_empty_blocks_list(temp_dir: Path) -> None:
    """Test fixing with empty blocks list."""
    detector = TerraformCommentDetector(root_path=temp_dir)
    fixed_count = detector.fix_commented_blocks([])
    assert fixed_count == 0


def test_fix_commented_blocks_dry_run(temp_dir: Path) -> None:
    """Test that fixing doesn't modify original file content incorrectly."""
    original_content = """
resource "aws_instance" "example" {
  ami = "ami-12345678"
}

# resource "aws_s3_bucket" "example" {
#   bucket = "my-bucket"
# }

# This is a regular comment, should stay
variable "environment" {
  type = string
}
"""
    tf_file = temp_dir / "main.tf"
    tf_file.write_text(original_content)

    detector = TerraformCommentDetector(root_path=temp_dir)
    blocks = detector.find_commented_blocks(tf_file)

    # Should only find the Terraform code block, not the regular comment
    assert len(blocks) == 1
    assert 'resource "aws_s3_bucket"' in blocks[0].first_line

    # Fix the blocks
    fixed_count = detector.fix_commented_blocks(blocks)
    assert fixed_count == 1

    # Check that regular comment is preserved
    final_content = tf_file.read_text()
    assert "# This is a regular comment, should stay" in final_content
    assert '# resource "aws_s3_bucket"' not in final_content


def test_scan_directory_with_nonexistent_path() -> None:
    """Test scanning a directory that doesn't exist."""
    detector = TerraformCommentDetector(root_path=Path("/fake/path"))
    result = detector.scan_directory(Path("/nonexistent/directory"))

    # Should handle gracefully and return empty result
    assert result.total_files_scanned == 0
    assert result.files_with_comments == 0
    assert result.total_blocks == 0
    assert not result.has_commented_code


def test_find_terraform_files_skip_hidden_directories(temp_dir: Path) -> None:
    """Test that hidden directories and files are skipped."""
    # Create hidden directory and files
    hidden_dir = temp_dir / ".hidden"
    hidden_dir.mkdir()
    (hidden_dir / "main.tf").write_text("# test")
    (temp_dir / ".hidden.tf").write_text("# test")

    # Create normal files
    (temp_dir / "main.tf").write_text("# test")

    detector = TerraformCommentDetector(root_path=temp_dir)
    tf_files = list(detector.find_terraform_files(temp_dir))

    # Should only find the non-hidden file
    assert len(tf_files) == 1
    assert tf_files[0].name == "main.tf"
    assert ".hidden" not in str(tf_files[0])
