# detect-commented-terraform

Detect commented-out Terraform code in your codebase and prevent it from being committed. This tool can be used as a pre-commit hook or as a standalone CLI. It scans `.tf` files for commented lines or blocks that look like Terraform resources, variables, or configuration, helping you keep your infrastructure code clean and production-ready.

## Features

- Detects commented-out Terraform resources, variables, assignments, and blocks
- Works as a pre-commit hook or CLI
- Scans all `.tf` files in your repository
- Easy to install from PyPI or use with pre-commit

## Installation (PyPI)

```sh
uv pip install detect-commented-terraform
# or
pip install detect-commented-terraform
```

## Usage as a Pre-commit Hook

Add to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/thetestlabs/detect-commented-terraform
  rev: v1.0.0  # Replace with the latest tag or commit hash
  hooks:
    - id: detect-commented-terraform
```

Then run:

```sh
pre-commit install
```

## CLI Usage

You can also run the hook manually:

```sh
detect-commented-terraform
# or
python -m detect_commented_terraform.cli
```

## How it works

- Scans all `.tf` files in your repository
- Flags any line or block that looks like commented-out Terraform code
- Exits with a nonzero code if any are found (blocks commit if used as a hook)

## Local Development

Run tests (if you add them):

```sh
pytest
```

## License

MIT License. See [LICENSE](LICENSE).
