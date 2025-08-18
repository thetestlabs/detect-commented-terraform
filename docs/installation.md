# Installation

## Requirements

- Python 3.9 or higher (recommended: Python 3.13)
- pip or uv package manager

## Install from PyPI

The easiest way to install `detect-commented-terraform` is from PyPI:

```bash
pip install detect-commented-terraform
```

## Install with uv

If you're using [uv](https://github.com/astral-sh/uv) for package management:

```bash
uv add detect-commented-terraform
```

## Install from Source

To install the latest development version:

```bash
git clone https://github.com/thetestlabs/detect-commented-terraform.git
cd detect-commented-terraform
uv sync
```

## Development Installation

For development work:

```bash
git clone https://github.com/thetestlabs/detect-commented-terraform.git
cd detect-commented-terraform
uv sync --dev
pre-commit install
```

This will install:

- All runtime dependencies
- Development dependencies (pytest, ruff, mypy, etc.)
- Pre-commit hooks

## Verify Installation

Test that the installation was successful:

```bash
detect-commented-terraform --help
```

You should see the help message with available commands.

## Dependencies

The core runtime dependencies are:

- [typer](https://typer.tiangolo.com/) - Modern CLI framework
- [rich](https://rich.readthedocs.io/) - Rich text and beautiful formatting
- [loguru](https://loguru.readthedocs.io/) - Structured logging

Development dependencies include:

- pytest - Testing framework
- ruff - Code formatting, import sorting, and linting
- mypy - Type checking
- pre-commit - Git hooks

## Docker

You can also run the tool using Docker:

```bash
docker run --rm -v $(pwd):/workspace ghcr.io/thetestlabs/detect-commented-terraform:latest scan /workspace
```

## Troubleshooting

### Permission Errors

If you encounter permission errors during installation:

```bash
pip install --user detect-commented-terraform
```

### Path Issues

Make sure the installed binary is in your PATH:

```bash
echo $PATH
which detect-commented-terraform
```

### Virtual Environment

It's recommended to install in a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install detect-commented-terraform
```
