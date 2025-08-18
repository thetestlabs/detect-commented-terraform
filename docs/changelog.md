# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documentation for ReadTheDocs deployment
- Comprehensive API documentation
- Contributing guidelines
- Development setup instructions

## [0.1.0] - 2025-07-09

### Added
- Initial release of detect-commented-terraform
- CLI tool with `scan` and `version` commands
- Smart detection of commented Terraform code blocks
- Beautiful terminal output using Rich library
- Structured logging with Loguru
- Pre-commit hook integration
- `--fix` option to automatically remove commented code
- Support for `.tf` and `.tfvars` files
- Comprehensive test suite with 78% coverage
- Modern Python package structure using uv
- CI/CD ready with proper exit codes

### Features
- **Smart Pattern Recognition**: Identifies Terraform keywords and code patterns
- **Automatic Fixing**: Remove commented code with `--fix` option
- **Detailed Reporting**: Shows filename, line numbers, and code preview
- **Modern CLI**: Built with Typer and Rich for excellent user experience
- **Git Integration**: Works as pre-commit hook
- **Fast Performance**: Efficient scanning with minimal overhead

### CLI Commands
- `detect-commented-terraform scan [PATH]` - Scan for commented code
- `detect-commented-terraform version` - Show version information

### CLI Options
- `--verbose, -v` - Enable verbose logging
- `--fix` - Automatically remove commented code blocks
- `--exit-code/--no-exit-code` - Control exit code behavior

### Pre-commit Hook
- Integrates with pre-commit framework
- Processes only changed Terraform files
- Provides clear feedback on issues found

### Detection Capabilities
- Detects commented out resources, variables, outputs
- Identifies commented assignments and blocks
- Ignores regular comments and documentation
- Handles multi-line commented blocks
- Preserves file structure when fixing

### Technical Details
- Python 3.9+ support
- Dependencies: typer, rich, loguru
- Modern package management with uv
- Comprehensive type hints
- Extensive test coverage
- Ready for PyPI publication

## [0.0.1] - 2025-07-09

### Added
- Initial project structure
- Basic Terraform comment detection logic
- Core models and data structures

---

## Release Notes

### v0.1.0 - Initial Release

This is the first stable release of detect-commented-terraform! 🎉

**Key Features:**
- **Smart Detection**: Accurately identifies commented Terraform code
- **Beautiful CLI**: Rich terminal output with tables and colors
- **Auto-Fix**: Automatically remove commented code with `--fix`
- **Git Integration**: Pre-commit hook support
- **Modern Python**: Built with latest tools and best practices

**What's Included:**
- Complete CLI tool with scan and version commands
- Pre-commit hook for Git workflow integration
- Comprehensive test suite (78% coverage)
- Documentation and examples
- Ready for PyPI distribution

**Quick Start:**
```bash
pip install detect-commented-terraform
detect-commented-terraform scan
```

**Pre-commit Setup:**
```yaml
repos:
  - repo: https://github.com/thetestlabs/detect-commented-terraform
    rev: v0.1.0
    hooks:
      - id: detect-commented-terraform
```

**Migration Notes:**
- This is the first release, no migration needed
- All APIs are stable and ready for production use

**Known Limitations:**
- Currently supports only `.tf` and `.tfvars` files
- Detection is based on syntax patterns (not semantic analysis)
- No configuration file support (CLI options only)

**Community:**
- Star the project on GitHub
- Report issues and feature requests
- Contribute to the project
- Share your success stories

Thank you for using detect-commented-terraform! 🚀
