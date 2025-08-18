# Usage

## Command Line Interface

The `detect-commented-terraform` CLI provides a simple and powerful interface for detecting and fixing commented out Terraform/OpenTofu/Terragrunt code.

### Supported File Types

- **Terraform**: `.tf` and `.tfvars` files
- **OpenTofu**: `.tf`, `.tofu` and `.tfvars` files
- **Terragrunt**: `.hcl` files

### Basic Commands

#### Scan Command

The main command for scanning IaC files:

```bash
detect-commented-terraform scan [PATH] [OPTIONS]
```

**Arguments:**
- `PATH` (optional): Directory to scan. Defaults to current directory.

**Options:**
- `--verbose, -v`: Enable verbose logging
- `--fix`: Automatically remove commented code blocks
- `--exit-code/--no-exit-code`: Exit with code 1 if commented code is found (default: true)

#### Version Command

Display version information:

```bash
detect-commented-terraform version
```

### Examples

#### Basic Scanning

Scan the current directory:

```bash
detect-commented-terraform scan
```

Scan a specific directory:

```bash
detect-commented-terraform scan /path/to/iac/files
```

#### Verbose Output

Enable detailed logging:

```bash
detect-commented-terraform scan --verbose
```

#### Automatic Fixing

Remove commented code automatically:

```bash
detect-commented-terraform scan --fix
```

```{warning}
The `--fix` option will permanently remove commented code from your files. Make sure to commit your changes or backup your files before using this option.
```

#### CI/CD Integration

For continuous integration, you might want to scan without exiting on errors:

```bash
detect-commented-terraform scan --no-exit-code
```

## Pre-commit Hook

The tool can be integrated into your Git workflow using pre-commit hooks.

### Basic Setup

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/thetestlabs/detect-commented-terraform
    rev: v1.0.0 # Use the latest version
    hooks:
      - id: detect-commented-terraform
```

### Custom Configuration

You can customize the pre-commit hook behavior:

```yaml
repos:
  - repo: https://github.com/thetestlabs/detect-commented-terraform
    rev: v1.0.0
    hooks:
      - id: detect-commented-terraform
        args: ["scan", "--verbose"]
        files: \.(tf|tfvars)$
```

### Local Installation

For local development, you can use the hook without external dependencies:

```yaml
repos:
  - repo: local
    hooks:
      - id: detect-commented-terraform
        name: Detect commented Terraform code
        entry: detect-commented-terraform
        language: python
        files: \.(tf|tfvars)$
        pass_filenames: false
        args: ["scan", "--exit-code"]
```

## Output Examples

### Successful Scan

When no commented code is found:

```
✅ No commented Terraform code found!
```

### Issues Found

When commented code is detected:

```
❌ Found 3 commented code block(s) in 2 file(s)

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File             ┃ Line(s) ┃ First Line                                       ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ main.tf          │ 18-20   │ # resource "aws_instance" "web" {                │
│ main.tf          │ 32-37   │ # resource "aws_s3_bucket_versioning" "example" { │
│ terraform.tfvars │ 6       │ # instance_count = 3                             │
└──────────────────┴─────────┴──────────────────────────────────────────────────┘
```

### Fix Mode

When using `--fix` option:

```
🔧 Fixing commented code blocks...
✅ Fixed 3 commented code block(s) in 2 file(s)
```

## File Types Supported

The tool automatically detects and processes:

- `.tf` files (Terraform configuration)
- `.tfvars` files (Terraform variables)

## Detection Logic

The tool uses smart pattern recognition to identify commented Terraform code:

### What Gets Detected

✅ **Commented Resources:**
```hcl
# resource "aws_instance" "example" {
#   ami = "ami-12345678"
# }
```

✅ **Commented Variables:**
```hcl
# variable "environment" {
#   type = string
# }
```

✅ **Commented Outputs:**
```hcl
# output "instance_id" {
#   value = aws_instance.example.id
# }
```

✅ **Commented Assignments:**
```hcl
# instance_type = "t2.micro"
# bucket_name = "my-bucket"
```

### What Gets Ignored

❌ **Regular Comments:**
```hcl
# This is a documentation comment
# TODO: Add more security groups
```

❌ **Special Comments:**
```hcl
# FIXME: Update AMI ID
# NOTE: This requires VPC setup
# HACK: Temporary workaround
```

❌ **Active Code:**
```hcl
resource "aws_instance" "example" {
  ami = "ami-12345678"
}
```

## Configuration

Currently, the tool doesn't require additional configuration files. All options are provided via command-line arguments.

## Exit Codes

The tool uses standard exit codes:

- `0`: Success (no commented code found or successfully fixed)
- `1`: Issues found (commented code detected)
- `2`: Error (invalid arguments, file not found, etc.)

## Performance

The tool is designed to be fast and efficient:

- Processes files in parallel where possible
- Uses efficient regex patterns for detection
- Minimal memory footprint
- Suitable for large Terraform codebases

## Integration with IDEs

### VS Code

You can integrate the tool with VS Code using tasks:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Scan Terraform Comments",
            "type": "shell",
            "command": "detect-commented-terraform",
            "args": ["scan", "--verbose"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        }
    ]
}
```

### Other IDEs

Most IDEs that support external tools can be configured to run the scan command. Check your IDE's documentation for "External Tools" or "Custom Commands".
