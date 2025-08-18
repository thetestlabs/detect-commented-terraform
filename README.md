<h2 align="center">Remove Commented Out Terraform Code From Your Codebase</h2>

[![CI](https://github.com/thetestlabs/detect-commented-terraform/actions/workflows/ci.yml/badge.svg)](https://github.com/thetestlabs/detect-commented-terraform/actions/workflows/ci.yml)
[![Test Coverage](https://github.com/thetestlabs/detect-commented-terraform/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/thetestlabs/detect-commented-terraform/actions/workflows/test-coverage.yml)
[![Docs](https://github.com/thetestlabs/detect-commented-terraform/actions/workflows/docs.yml/badge.svg)](https://github.com/thetestlabs/detect-commented-terraform/actions/workflows/docs.yml)
[![PyPI version](https://badge.fury.io/py/detect-commented-terraform.svg)](https://badge.fury.io/py/detect-commented-terraform)
[![Python Compatibility](https://img.shields.io/pypi/pyversions/detect-commented-terraform)](https://pypi.org/project/detect-commented-terraform/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![GitHub commits since latest release](https://img.shields.io/github/commits-since/thetestlabs/detect-commented-terraform/latest/main)
[![codecov](https://codecov.io/gh/thetestlabs/detect-commented-terraform/graph/badge.svg?token=0KJTZE0WBN)](https://codecov.io/gh/thetestlabs/detect-commented-terraform)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2fe5d56033444e3fa7dae687515d710c)](https://app.codacy.com/gh/thetestlabs/detect-commented-terraform/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/2fe5d56033444e3fa7dae687515d710c)](https://app.codacy.com/gh/thetestlabs/detect-commented-terraform/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

---

**📖 [Complete Documentation on ReadTheDocs](https://detect-commented-terraform.readthedocs.io/en/latest/)**

---

## Quick Start

### Installation

```bash
pip install detect-commented-terraform
```

### Basic Usage

Scan your current directory for commented out Terraform code:

```bash
detect-commented-terraform scan
```

Scan a specific directory:

```bash
detect-commented-terraform scan /path/to/iac/files
```

**Supported formats:**

- Terraform (`.tf`, `.tfvars`)
- OpenTofu (`.tf`, `.tofu`, `.tfvars`)
- Terragrunt (`.hcl`)

### GitHub Action

Add to your workflow to automatically check for commented IaC code:

```yaml
name: Check Commented Out Terraform Code
on: [push, pull_request]

jobs:
  check-iac:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Detect commented IaC code
        uses: thetestlabs/detect-commented-terraform@v1
        with:
          path: "./infrastructure"
```

### Pre-commit Hook

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/thetestlabs/detect-commented-terraform
    rev: v1.0.0 # Use the latest version
    hooks:
      - id: detect-commented-terraform
```

## What it detects

The tool identifies commented out Terraform/OpenTofu/Terragrunt Code patterns such as:

**Terraform/OpenTofu:**

```hcl
# resource "aws_instance" "example" {
#   ami           = "ami-12345678"
#   instance_type = "t2.micro"
# }

# variable "environment" {
#   description = "Environment name"
#   type        = string
# }
```

**Terragrunt:**

```hcl
# include {
#   path = find_in_parent_folders()
# }

# dependency "vpc" {
#   config_path = "../vpc"
# }

# inputs = {
#   environment = "production"
# }
```

It distinguishes between:

- ✅ Regular comments (ignored)
- ❌ Commented out code blocks (detected)

## Key Features

- 🔍 **Smart Detection**: Accurately identifies commented-out IaC code vs. regular comments
- 📝 **Detailed Reporting**: Shows filename, line numbers, and code preview
- 🚀 **CLI Integration**: Rich terminal output with multiple format options
- 🔧 **Pre-commit Ready**: Easy integration with pre-commit hooks
- 📊 **Multi-format Support**: Terraform (.tf, .tfvars), OpenTofu (.tf, .tofu, .tfvars), Terragrunt (.hcl)
- 🎨 **Beautiful Output**: Colored terminal output with Rich library

## CLI Options

```bash
detect-commented-terraform scan [PATH] [OPTIONS]

Options:
  --verbose, -v           Enable verbose logging
  --exit-code/--no-exit-code  Exit with code 1 if commented code found (default: true)
  --help                  Show help message
```

## Example Output

```
Scanning for commented Terraform code...

Found commented code in main.tf:
  Lines 15-18:
    # resource "aws_instance" "web" {
    #   ami           = "ami-12345678"
    #   instance_type = "t2.micro"
    # }

Summary: 1 file with commented code found
```

## Documentation

- **📖 [Full Documentation](https://detect-commented-terraform.readthedocs.io/en/latest/)** - Complete usage guide and API reference
- **🚀 [Installation Guide](https://detect-commented-terraform.readthedocs.io/en/latest/installation.html)** - Detailed installation instructions
- **💡 [Usage Examples](https://detect-commented-terraform.readthedocs.io/en/latest/usage.html)** - Comprehensive usage examples
- **🤝 [Contributing](https://detect-commented-terraform.readthedocs.io/en/latest/contributing.html)** - How to contribute to the project

## Support

- **🐛 [Issue Tracker](https://github.com/thetestlabs/detect-commented-terraform/issues)** - Report bugs or request features
- **💬 [Discussions](https://github.com/thetestlabs/detect-commented-terraform/discussions)** - Ask questions and share ideas
- **📧 [Security Issues](SECURITY.md)** - Report security vulnerabilities

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
