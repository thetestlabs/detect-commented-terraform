# detect-commented-terraform Documentation

Welcome to the documentation for **detect-commented-terraform**, a CLI tool and pre-commit hook to detect and optionally remove commented out Terraform/OpenTofu/Terragrunt code in your repository.

**Supports:**
- **Terraform** (`.tf`, `.tfvars`)
- **OpenTofu** (`.tf`, `.tofu`, `.tfvars`)
- **Terragrunt** (`.hcl`)

```{toctree}
:maxdepth: 2
:caption: Contents:

why-use-this-tool
installation
usage
api
contributing
ci-cd
changelog
```

## Quick Start

### Installation

```bash
pip install detect-commented-terraform
```

### Basic Usage

```bash
# Scan current directory for commented IaC code
detect-commented-terraform scan

# Scan and automatically fix issues
detect-commented-terraform scan --fix

# Scan with verbose output
detect-commented-terraform scan --verbose
```

### Pre-commit Hook

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/thetestlabs/detect-commented-terraform
    rev: v1.0.0  # Use the ref matching your desired version
    hooks:
      - id: detect-commented-terraform
```

## Features

- 🔍 **Smart Detection**: Identifies commented out Terraform code blocks
- 🛠️ **Automatic Fixing**: Remove commented code with `--fix` option
- 📝 **Detailed Reporting**: Shows filename, line numbers, and code preview
- 🚀 **CLI Tool**: Modern CLI with rich output formatting
- 🔧 **Pre-commit Integration**: Works seamlessly with git workflows
- 📊 **Comprehensive Coverage**: Supports `.tf` and `.tfvars` files

## What it Detects

The tool identifies commented out Terraform code patterns such as:

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

While ignoring regular comments:

```hcl
# This is a regular comment
# TODO: Add more resources
# NOTE: Check security groups
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
