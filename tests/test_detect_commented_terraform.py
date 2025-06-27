import subprocess
import sys
import shutil
from pathlib import Path

HOOK_SCRIPT = "detect_commented_terraform.py"


def get_hook_script_path():
    """Return the absolute path to the hook script in the project root."""
    # Try to find the script relative to this test file
    here = Path(__file__).parent.parent.resolve()
    script_path = here / HOOK_SCRIPT
    if not script_path.exists():
        raise FileNotFoundError(f"Could not find {HOOK_SCRIPT} at {script_path}")
    return script_path


def test_detects_commented_resource(tmp_path):
    """Should detect commented-out Terraform resource blocks and block the commit."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text("""
# resource "aws_instance" "example" {
#   ami           = "ami-123456"
#   instance_type = "t2.micro"
# }
""")
    # Copy the hook script into the temp directory
    script_path = tmp_path / HOOK_SCRIPT
    shutil.copyfile(get_hook_script_path(), script_path)
    result = subprocess.run(
        [sys.executable, HOOK_SCRIPT], cwd=tmp_path, capture_output=True, text=True, check=False
    )
    assert "Commented-out Terraform code detected" in result.stdout
    assert result.returncode == 1


def test_allows_clean_file(tmp_path):
    """Should allow clean Terraform files with no commented-out code."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text("""
resource "aws_instance" "example" {
  ami           = "ami-123456"
  instance_type = "t2.micro"
}
""")
    script_path = tmp_path / HOOK_SCRIPT
    shutil.copyfile(get_hook_script_path(), script_path)
    result = subprocess.run(
        [sys.executable, HOOK_SCRIPT], cwd=tmp_path, capture_output=True, text=True, check=False
    )
    assert "Commented-out Terraform code detected" not in result.stdout
    assert result.returncode == 0


def test_detects_commented_assignment(tmp_path):
    """Should detect commented-out Terraform assignments and block the commit."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text("""
# ami = "ami-123456"
# name = "example"
""")
    script_path = tmp_path / HOOK_SCRIPT
    shutil.copyfile(get_hook_script_path(), script_path)
    result = subprocess.run(
        [sys.executable, HOOK_SCRIPT], cwd=tmp_path, capture_output=True, text=True, check=False
    )
    assert "Commented-out Terraform code detected" in result.stdout
    assert result.returncode == 1
