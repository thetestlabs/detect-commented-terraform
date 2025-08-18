# Contributing

We welcome contributions to `detect-commented-terraform`! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.9 or higher (recommended: Python 3.13)
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Clone the Repository

```bash
git clone https://github.com/thetestlabs/detect-commented-terraform.git
cd detect-commented-terraform
```

### Install Dependencies

```bash
uv sync --dev
```

### Install Pre-commit Hooks

```bash
pre-commit install
```

## Quick Start for Contributors

1. **Fork** this repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/detect-commented-terraform.git
   cd detect-commented-terraform
   ```
3. **Create** a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make** your changes and add tests
5. **Run** the test suite:
   ```bash
   uv run pytest
   ```
6. **Commit** your changes using [conventional commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat: add your new feature"
   ```
7. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open** a Pull Request on GitHub

## Development Workflow

### Running Tests

Run the full test suite:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=src/detect_commented_terraform --cov-report=html
```

Run specific test file:

```bash
uv run pytest tests/test_detector.py
```

### Code Quality

Format and lint code:

```bash
uv run ruff format src tests
uv run ruff check src tests --fix
```

Type checking:

```bash
uv run mypy src
```

### Development Commands

Run all quality checks before committing:

```bash
# Format code
uv run ruff format src tests

# Lint code
uv run ruff check src tests

# Type check
uv run mypy src

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/detect_commented_terraform --cov-report=html
```

### Build and Package

Build the package:

```bash
uv build
```

Check the package:

```bash
uv run twine check dist/*
```

### Documentation

Build documentation locally:

```bash
cd docs
uv run sphinx-build -b html . _build/html
```

### Running Tests

Run the full test suite:

```bash
uv run python -m pytest
```

Run tests with coverage:

```bash
uv run python -m pytest --cov=src/detect_commented_terraform --cov-report=html
```

Run specific tests:

```bash
uv run python -m pytest tests/test_detector.py -v
```

### Code Quality

#### Formatting and Linting

Format and lint code with Ruff:

```bash
uv run ruff format src tests
uv run ruff check src tests --fix
```

#### Type Checking

Run mypy type checking:

```bash
uv run mypy src
```

### Using the Makefile

Common tasks are available through the Makefile:

```bash
make help          # Show available commands
make test          # Run tests
make lint          # Run linting
make format        # Format code
make format-check  # Check formatting
make clean         # Clean build artifacts
make build         # Build package
```

## Code Style

### Python Style Guide

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Maximum line length: 120 characters (Ruff default)
- Use descriptive variable and function names
- Include docstrings for all public functions and classes

### Example Code Style

```python
from typing import List, Optional
from pathlib import Path

def process_terraform_files(
    directory: Path,
    extensions: Optional[List[str]] = None
) -> List[Path]:
    """
    Process Terraform files in the given directory.

    Args:
        directory: Directory to scan for files
        extensions: List of file extensions to include

    Returns:
        List of Terraform file paths

    Raises:
        FileNotFoundError: If directory doesn't exist
    """
    if extensions is None:
        extensions = ['.tf', '.tfvars']

    terraform_files = []
    for ext in extensions:
        terraform_files.extend(directory.glob(f'**/*{ext}'))

    return terraform_files
```

### Docstring Style

Use Google-style docstrings:

```python
def find_commented_blocks(self, file_path: Path) -> List[CommentedCodeBlock]:
    """Find commented out code blocks in a single file.

    Args:
        file_path: Path to the Terraform file to scan

    Returns:
        List of commented code blocks found in the file

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read
    """
```

## Testing Guidelines

### Test Structure

Tests are organized by module:

```
tests/
├── conftest.py          # Test fixtures
├── test_detector.py     # Detector tests
├── test_cli.py          # CLI tests
└── test_models.py       # Model tests
```

### Writing Tests

#### Test Naming

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

#### Test Structure

```python
def test_feature_behavior(fixture_name: Type) -> None:
    """Test that feature behaves correctly."""
    # Arrange
    setup_data = create_test_data()

    # Act
    result = function_under_test(setup_data)

    # Assert
    assert result == expected_value
    assert len(result) == 1
```

#### Using Fixtures

```python
def test_with_temp_file(temp_dir: Path) -> None:
    """Test using temporary directory fixture."""
    test_file = temp_dir / "test.tf"
    test_file.write_text("# resource \"aws_instance\" \"test\" {}")

    detector = TerraformCommentDetector(root_path=temp_dir)
    blocks = detector.find_commented_blocks(test_file)

    assert len(blocks) == 1
```

### Test Coverage

Aim for high test coverage:

- New features should include comprehensive tests
- Bug fixes should include regression tests
- Edge cases should be tested
- Error conditions should be tested

## Documentation

### Docstring Documentation

All public functions and classes must have docstrings:

```python
class TerraformCommentDetector:
    """Detects commented out Terraform code in files.

    This class provides methods to scan Terraform files and identify
    blocks of commented out code based on Terraform syntax patterns.

    Attributes:
        root_path: Root directory for relative path calculations

    Example:
        >>> detector = TerraformCommentDetector(Path("/project"))
        >>> result = detector.scan_directory()
        >>> print(f"Found {result.total_blocks} commented blocks")
    """
```

### README Updates

When adding new features:

1. Update the main README.md
2. Add usage examples
3. Update the feature list
4. Add any new CLI options

### API Documentation

Update the API documentation in `docs/api.md` when:

- Adding new public methods
- Changing method signatures
- Adding new classes or modules

## Submitting Changes

### Pull Request Process

1. **Create a Feature Branch**

   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Make Your Changes**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Run Quality Checks**

   ```bash
   make format
   make lint
   make test
   ```

4. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "Add new feature: description"
   ```

5. **Push to GitHub**

   ```bash
   git push origin feature/new-feature-name
   ```

6. **Create Pull Request**
   - Go to GitHub and create a pull request
   - Fill out the PR template
   - Link any related issues

### Pull Request Guidelines

#### PR Title Format

Use conventional commit format:

- `feat: add new feature`
- `fix: resolve bug in detector`
- `docs: update API documentation`
- `test: add tests for CLI`
- `refactor: improve code structure`

#### PR Description

Include:

- Description of changes
- Motivation for changes
- Related issues
- Testing performed
- Breaking changes (if any)

#### Code Review Process

- All PRs require review before merging
- Address reviewer feedback promptly
- Keep PRs focused and reasonably sized
- Update documentation as needed

## Issue Guidelines

### Bug Reports

When reporting bugs, include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Minimal example code

### Feature Requests

When requesting features:

- Describe the use case
- Explain the benefit
- Provide examples if possible
- Consider implementation complexity

### Issue Labels

Common labels:

- `bug`: Something isn't working
- `enhancement`: New feature request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed

## Release Process

### Version Numbering

We use semantic versioning (SemVer):

- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

### Release Steps

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release commit
4. Tag the release
5. Push to GitHub
6. Create GitHub release
7. Publish to PyPI

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn
- Maintain professional communication

### Getting Help

- Check existing issues and documentation
- Ask questions in GitHub discussions
- Join our community chat (if available)
- Reach out to maintainers

## Recognition

Contributors are recognized in:

- `CONTRIBUTORS.md` file
- Release notes
- GitHub contributor insights
- Special thanks in major releases

Thank you for contributing to `detect-commented-terraform`! 🎉
