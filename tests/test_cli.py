import sys
import subprocess


from detect_commented_terraform.cli import scan_file
from detect_commented_terraform.cli import is_commented_terraform_line
from detect_commented_terraform.cli import find_commented_terraform_blocks


def run_cli(tmp_path, tf_content):
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(tf_content)
    result = subprocess.run(
        [sys.executable, "-m", "detect_commented_terraform.cli"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    return result


def test_detects_commented_resource(tmp_path):
    """Should detect commented-out Terraform resource blocks and exit nonzero."""
    tf_content = """
# resource "aws_instance" "example" {
#   ami           = "ami-123456"
#   instance_type = "t2.micro"
# }
"""
    result = run_cli(tmp_path, tf_content)
    assert "Commented-out Terraform code detected" in result.stdout
    assert result.returncode == 1


def test_allows_clean_file(tmp_path):
    """Should allow clean Terraform files and exit zero."""
    tf_content = """
resource "aws_instance" "example" {
  ami           = "ami-123456"
  instance_type = "t2.micro"
}
"""
    result = run_cli(tmp_path, tf_content)
    assert "Commented-out Terraform code detected" not in result.stdout
    assert result.returncode == 0


def test_detects_commented_assignment(tmp_path):
    """Should detect commented-out Terraform assignments and exit nonzero."""
    tf_content = """
# ami = "ami-123456"
# name = "example"
"""
    result = run_cli(tmp_path, tf_content)
    assert "Commented-out Terraform code detected" in result.stdout
    assert result.returncode == 1


def test_detects_commented_block_inside_code(tmp_path):
    """Should detect a single commented-out line inside a resource block."""
    tf_content = """
resource "aws_instance" "example" {
  ami           = "ami-123456"
  # instance_type = "t2.micro"
}
"""
    result = run_cli(tmp_path, tf_content)
    assert "Commented-out Terraform code detected" in result.stdout
    assert result.returncode == 1


def test_detects_multiline_block_comment(tmp_path):
    """Should detect commented-out Terraform code inside /* ... */ block comments."""
    tf_content = """
/*
resource "aws_instance" "example" {
  ami           = "ami-123456"
  instance_type = "t2.micro"
}
*/
"""
    result = run_cli(tmp_path, tf_content)
    assert "Commented-out Terraform code detected" in result.stdout
    assert result.returncode == 1


def test_is_commented_terraform_line():
    """Unit test for is_commented_terraform_line function."""
    assert is_commented_terraform_line('# resource "aws_instance" "example" {')
    assert is_commented_terraform_line('# ami = "ami-123456"')
    assert not is_commented_terraform_line('ami = "ami-123456"')
    assert not is_commented_terraform_line('resource "aws_instance" "example" {')


def test_find_commented_terraform_blocks():
    """Unit test for find_commented_terraform_blocks function."""
    lines = [
        '# resource "aws_instance" "example" {',
        '#   ami = "ami-123456"',
        "# }",
    ]
    assert find_commented_terraform_blocks(lines) == [0]
    lines2 = [
        'resource "aws_instance" "example" {',
        '  ami = "ami-123456"',
        "}",
    ]
    assert find_commented_terraform_blocks(lines2) == []


def test_scan_file(tmp_path):
    """Unit test for scan_file function."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text("""
# resource "aws_instance" "example" {
#   ami           = "ami-123456"
#   instance_type = "t2.micro"
# }
""")
    warnings = scan_file(tf_file)
    assert any("Commented-out Terraform code detected" in w for w in warnings)
