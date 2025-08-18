# CI/CD and Automation

This project includes comprehensive GitHub Actions workflows for automated testing, documentation, and releases.

## Workflow Overview

### 🔄 Workflow Coordination

The CI/CD system uses GitHub Actions `workflow_run` triggers to ensure proper execution order:

- **Release → Documentation**: Documentation workflow waits for release completion to pick up new version tags
- **Sequential Processing**: Prevents concurrent execution that could cause version synchronization issues
- **Error Handling**: Each workflow can run independently if needed for debugging

### 🔄 Continuous Integration (CI)

**Trigger**: On PR creation and push to main
**Workflow**: `.github/workflows/ci.yml`

- **Linting & Formatting**: Python (Ruff), YAML, Markdown, JSON, TOML
- **Type Checking**: mypy static type analysis
- **Security Scanning**: bandit vulnerability checks
- **Build Verification**: Package building and validation

### 🧪 Test Coverage

**Trigger**: On push, PR creation/synchronization, and manual dispatch
**Workflow**: `.github/workflows/test-coverage.yml`

- **Comprehensive Testing**: pytest across Python 3.9-3.13
- **Coverage Analysis**: Branch coverage reporting with coverage.xml and HTML
- **Codecov Integration**: Automated coverage reporting
- **Codacy Integration**: Additional coverage analysis
- **Artifact Storage**: Coverage reports preserved for 30 days

### 📚 Documentation

**Trigger**: On main branch changes to docs, source code, or README, OR after Release workflow completion
**Workflow**: `.github/workflows/docs.yml`

- **Sequential Execution**: Waits for release workflow to complete before running to ensure version synchronization
- **Sphinx Build**: Automated documentation building with warnings as errors
- **GitHub Pages**: Automatic deployment to GitHub Pages
- **ReadTheDocs**: Automatic build triggering for ReadTheDocs.io
- **PR Comments**: Automated preview links on pull requests
- **Artifact Storage**: Documentation artifacts preserved for 30 days

### 🔍 PR Comprehensive Checks

**Trigger**: On PR creation, synchronization, or reopening
**Workflow**: `.github/workflows/pr-checks.yml`

- **All File Type Linting**: Python, YAML, Markdown, JSON, TOML validation
- **Security Checks**: Common issue detection (TODOs, print statements, potential secrets)
- **Pre-commit Hooks**: Full pre-commit suite execution
- **Package Verification**: Build and installation testing
- **Automated PR Comments**: Status updates on PR checks

### 🚀 Release Management

**Trigger**: On main branch push (excluding docs/changelog changes)
**Workflow**: `.github/workflows/release.yml`

- **Semantic Versioning**: Automated version bumping based on commit messages
- **Version Synchronization**: Custom script updates all version references across documentation files
- **Changelog Generation**: Automatic CHANGELOG.md updates
- **Git Tagging**: Semantic release tags with GitHub releases
- **PyPI Publishing**: Automated package publishing to PyPI
- **Release Notes**: Rich release notes with usage examples
- **Workflow Coordination**: Triggers documentation workflow after completion for synchronized updates

## Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning:

- `feat:` - New features (minor version bump)
- `fix:` - Bug fixes (patch version bump)
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions or changes
- `chore:` - Maintenance tasks

**Breaking Changes**: Add `BREAKING CHANGE:` in commit body for major version bumps.

## Development Workflow Commands

```bash
# Setup development environment
uv sync --dev

# Run all checks before committing
uv run ruff format src tests
uv run ruff check src tests
uv run mypy src
uv run pytest

# Run tests with branch coverage (matches CI)
uv run pytest --cov=src/detect_commented_terraform --cov-branch --cov-report=html

# Run tests with comprehensive coverage reporting
uv run pytest \
  --cov=src/detect_commented_terraform \
  --cov-branch \
  --cov-report=xml \
  --cov-report=html

# Build documentation locally
cd docs && uv run sphinx-build -b html . _build/html

# Build package
uv build
```

## Automated Quality Assurance

### Code Quality Tools

- **Ruff**: Python linting and formatting
- **mypy**: Static type checking
- **bandit**: Security vulnerability scanning
- **yamllint**: YAML file validation
- **markdownlint**: Markdown file validation

### Testing Strategy

- **Dedicated Test Workflow**: Separate `test-coverage` workflow for comprehensive testing
- **Unit Tests**: Comprehensive test coverage with pytest
- **Integration Tests**: End-to-end workflow testing
- **Cross-Platform**: Testing across Python 3.9-3.13 on all events (push, PR, manual)
- **Branch Coverage**: Detailed coverage analysis including branch coverage
- **Coverage Reporting**: Dual integration with Codecov and Codacy for comprehensive tracking
- **Artifact Preservation**: Coverage reports stored as GitHub Actions artifacts

### Release Process

1. **Automated Versioning**: Based on conventional commit messages
2. **Version Synchronization**: Custom script (`scripts/update_version.py`) updates all version references in:
   - `pyproject.toml` (package version)
   - `src/detect_commented_terraform/__init__.py` (Python package)
   - `README.md` (pre-commit hook examples)
   - `docs/*.md` files (documentation examples)
   - `.pre-commit-hooks.yaml` (if applicable)
3. **Changelog Generation**: Automatic updates with semantic-release
4. **Package Building**: Automated wheel and source distribution creation
5. **PyPI Publishing**: Secure publishing with trusted publishing
6. **GitHub Releases**: Rich release notes with download links
7. **Documentation Update**: Triggers docs workflow for ReadTheDocs synchronization

### Security and Compliance

- **Dependency Scanning**: Automated vulnerability detection
- **Security Linting**: bandit security checks
- **Pre-commit Hooks**: Comprehensive validation before commits
- **Branch Protection**: Required status checks and reviews
