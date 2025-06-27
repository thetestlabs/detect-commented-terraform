# detect-commented-terraform

Detect commented-out Terraform code in your codebase and prevent it from being committed. This pre-commit hook scans `.tf` files for commented lines that look like Terraform resources, variables, or configuration, helping you keep your infrastructure code clean and production-ready.

[![PyPI version](https://img.shields.io/pypi/v/detect-commented-terraform.svg)](https://pypi.org/project/detect-commented-terraform/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/detect-commented-terraform.svg)](https://pypi.org/project/detect-commented-terraform/)
[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg)](https://opensource.org/licenses/MIT)

## Features

- Blocks commits if commented-out Terraform code is detected
- Scans staged `.tf` files for commented lines that look like code (resources, variables, assignments, etc.)
- Easy to use with [pre-commit](https://pre-commit.com/)
- Can be installed as a CLI or pre-commit hook via PyPI or GitHub

## Installation (PyPI)

```sh
pip install detect-commented-terraform
```

## Usage as a Pre-commit Hook

### 1. Add to your `.pre-commit-config.yaml`

**From PyPI:**

```yaml
- repo: https://github.com/thetestlabs/detect-commented-terraform
  rev: v1.0.0  # Replace with the latest tag or commit hash
  hooks:
    - id: detect-commented-terraform
```

**Or, using PyPI packaging:**

```yaml
- repo: https://pypi.org/project/detect-commented-terraform
  rev: v1.0.0  # Replace with the latest version
  hooks:
    - id: detect-commented-terraform
```

### 2. Install pre-commit hooks

```sh
pre-commit install
```

### 3. Try to commit a `.tf` file with commented-out code

The commit will be blocked and the offending lines will be shown.

## CLI Usage

You can also run the hook manually:

```sh
python detect_commented_terraform.py
# or, if installed via pip
python -m detect_commented_terraform
```

## Publishing to PyPI

1. Update the version in `pyproject.toml`.
2. Build the package:

   ```sh
   python -m build
   ```

3. Publish to PyPI:

   ```sh
   python -m twine upload dist/*
   ```

## Local Development

Run tests:

```sh
pytest
```

## License

MIT License. See [LICENSE](LICENSE).
