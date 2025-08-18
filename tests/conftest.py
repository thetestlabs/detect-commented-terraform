"""Test configuration and fixtures."""

from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """Create a temporary directory for testing."""
    with TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_terraform_file(temp_dir: Path) -> Path:
    """Create a sample Terraform file with some commented code."""
    tf_content = """
# This is a comment
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}

# resource "aws_s3_bucket" "example" {
#   bucket = "my-bucket"
# }

variable "environment" {
  description = "Environment name"
  type        = string
}

# variable "region" {
#   description = "AWS region"
#   type        = string
#   default     = "us-east-1"
# }

output "instance_id" {
  value = aws_instance.example.id
}
"""

    tf_file = temp_dir / "main.tf"
    tf_file.write_text(tf_content)
    return tf_file
