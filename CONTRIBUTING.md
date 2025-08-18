# Contributing to detect-commented-terraform

Thank you for your interest in contributing to detect-commented-terraform! We welcome contributions from the community.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Python 3.9 or higher (recommended: Python 3.13)
- [uv](https://github.com/astral-sh/uv) for dependency management
- Git

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   ```bash
   git clone https://github.com/your-username/detect-commented-terraform.git
   cd detect-commented-terraform
   ```

3. **Set up the development environment**:

   ```bash
   make dev-install
   ```

4. **Verify the setup**:

   ```bash
   make test
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Run tests and checks**:

   ```bash
   make check          # Run all checks
   make test           # Run tests
   make test-cov       # Run tests with coverage
   make lint           # Run linting
   make format         # Format code
   ```

4. **Commit your changes** using conventional commits:

   ```bash
   git commit -m "feat: add new feature description"
   ```

5. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**

```
feat: add --fix option to remove commented code
fix: handle empty terraform files correctly
docs: update installation instructions
test: add integration tests for CLI
```

## Code Standards

### Python Code Style

- **Formatting & Linting**: We use [Ruff](https://docs.astral.sh/ruff/) for code formatting, import sorting, and linting
- **Type hints**: We use [mypy](https://mypy.readthedocs.io/) for static type checking

### Documentation

- **Docstrings**: Use Google-style docstrings
- **Type hints**: All functions should have proper type hints
- **README**: Keep documentation up to date

### Testing

- **Unit tests**: Write tests for new functionality
- **Integration tests**: Test end-to-end workflows
- **Coverage**: Aim for high test coverage
- **Markers**: Use pytest markers for different test types

## Project Structure

```
detect-commented-terraform/
├── src/detect_commented_terraform/  # Main package
│   ├── __init__.py
│   ├── cli.py                      # CLI interface
│   ├── detector.py                 # Core detection logic
│   ├── models.py                   # Data models
│   └── pre_commit.py               # Pre-commit integration
├── tests/                          # Test suite
├── docs/                           # Documentation
├── examples/                       # Example files
├── .github/                        # GitHub workflows and templates
├── pyproject.toml                  # Project configuration
├── Makefile                        # Development commands
└── README.md                       # Main documentation
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run tests in parallel
make test-parallel

# Run specific test types
pytest -m "not slow"           # Skip slow tests
pytest -m "integration"        # Run integration tests only
pytest -m "unit"              # Run unit tests only
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Follow the AAA pattern (Arrange, Act, Assert)
- Use pytest fixtures for common setup
- Mark slow tests with `@pytest.mark.slow`

### Test Coverage

We aim for high test coverage. Check coverage with:

```bash
make test-cov
open htmlcov/index.html  # View coverage report
```

## Documentation

### Building Documentation

```bash
make docs        # Build documentation
make docs-serve  # Serve documentation locally
```

### Writing Documentation

- Use Markdown for documentation files
- Keep README.md up to date
- Document new features and changes
- Include usage examples

## Security

### Security Considerations

- Never commit secrets or sensitive data
- Use secure coding practices
- Run security checks: `make check-security`
- Report security issues privately

### Dependency Management

- Keep dependencies up to date
- Use `uv` for dependency management
- Pin versions in `pyproject.toml`
- Review dependency security with `safety`

## Release Process

Releases are automated through GitHub Actions:

1. **Semantic versioning** based on conventional commits
2. **Automatic changelog** generation
3. **GitHub releases** with artifacts
4. **PyPI publishing** for distribution

## Getting Help

- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers directly for sensitive issues

## Recognition

Contributors are recognized in our:

- GitHub contributors list
- Release notes
- Documentation acknowledgments

Thank you for contributing to detect-commented-terraform! 🚀
