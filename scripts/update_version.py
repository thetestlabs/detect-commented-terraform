#!/usr/bin/env python3
"""Script to update version in pyproject.toml and documentation files for semantic-release."""

import re
import sys
from pathlib import Path

import toml


def update_version_in_file(file_path: Path, old_version: str, version: str) -> bool:
    """Update version references in a file."""
    if not file_path.exists():
        print(f"  ⚠️  File not found: {file_path}")
        return False

    try:
        content = file_path.read_text(encoding="utf-8")
        updated_content = content
        changes_made = False

        # Pattern 1: YAML rev fields (pre-commit hooks)
        pattern1 = rf"rev:\s*v{re.escape(old_version)}"
        replacement1 = f"rev: v{version}"
        new_content = re.sub(pattern1, replacement1, updated_content)
        if new_content != updated_content:
            updated_content = new_content
            changes_made = True
            print(f"  📌 Updated rev: pattern in {file_path}")

        # Pattern 2: Version references in text (like "v1.0.0" in documentation)
        pattern2 = rf"\bv{re.escape(old_version)}\b"
        replacement2 = f"v{version}"
        new_content = re.sub(pattern2, replacement2, updated_content)
        if new_content != updated_content:
            updated_content = new_content
            changes_made = True
            print(f"  📌 Updated version reference in {file_path}")

        # Pattern 3: Installation examples (pip install package==version)
        pattern3 = rf"detect-commented-terraform=={re.escape(old_version)}"
        replacement3 = f"detect-commented-terraform=={version}"
        new_content = re.sub(pattern3, replacement3, updated_content)
        if new_content != updated_content:
            updated_content = new_content
            changes_made = True
            print(f"  📌 Updated pip install version in {file_path}")

        if changes_made:
            file_path.write_text(updated_content, encoding="utf-8")
            print(f"✅ Updated version in {file_path}")
            return True
        else:
            print(f"  📄 No version references found in {file_path}")
            return False

    except (OSError, UnicodeDecodeError, re.error) as e:
        print(f"  ❌ Error updating {file_path}: {e}")
        return False


def update_pyproject_toml(pyproject_path: Path, version: str) -> str:
    """Update version in pyproject.toml and return old version."""
    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found")
        sys.exit(1)

    # Read current pyproject.toml
    try:
        with pyproject_path.open(encoding="utf-8") as f:
            data = toml.load(f)
    except (OSError, toml.TomlDecodeError) as e:
        print(f"Error reading pyproject.toml: {e}")
        sys.exit(1)

    # Update version
    old_version: str = str(data["project"]["version"])
    data["project"]["version"] = version

    # Write back to file
    try:
        with pyproject_path.open("w", encoding="utf-8") as f:
            toml.dump(data, f)
    except OSError as e:
        print(f"Error writing pyproject.toml: {e}")
        sys.exit(1)

    print(f"✅ Updated version in pyproject.toml: {old_version} → {version}")
    return old_version


def update_documentation_files(repo_root: Path, old_version: str, version: str) -> list[str]:
    """Update version references in documentation files."""
    doc_files = [
        repo_root / "README.md",
        repo_root / "docs" / "index.md",
        repo_root / "docs" / "why-use-this-tool.md",
        repo_root / "docs" / "usage.md",
        repo_root / "docs" / "installation.md",
        repo_root / ".pre-commit-hooks.yaml",
    ]

    print(f"\n🔍 Searching for version {old_version} to update to {version}...")
    updated_files = []
    for doc_file in doc_files:
        print(f"  Checking {doc_file}...")
        if update_version_in_file(doc_file, old_version, version):
            updated_files.append(str(doc_file.name))

    return updated_files


def update_init_py(repo_root: Path, version: str) -> None:
    """Update version in __init__.py file."""
    init_path = repo_root / "src" / "detect_commented_terraform" / "__init__.py"
    if not init_path.exists():
        print("⚠️  __init__.py not found")
        return

    try:
        with init_path.open(encoding="utf-8") as f:
            content = f.read()

        # Replace version line (without 'v' prefix for Python package version)
        lines = content.split("\n")
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("__version__"):
                lines[i] = f'__version__ = "{version}"'
                updated = True
                break

        if updated:
            with init_path.open("w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            print(f"✅ Updated __init__.py version to {version}")
        else:
            print("⚠️  __version__ line not found in __init__.py")

    except (OSError, UnicodeDecodeError) as e:
        print(f"❌ Error updating __init__.py: {e}")


def update_version(version: str) -> None:
    """Update version in pyproject.toml and documentation files."""
    repo_root = Path(__file__).parent.parent
    pyproject_path = repo_root / "pyproject.toml"

    # Update pyproject.toml and get old version
    old_version = update_pyproject_toml(pyproject_path, version)

    # Update documentation files
    updated_files = update_documentation_files(repo_root, old_version, version)

    # Report documentation updates
    if updated_files:
        print(f"\n📚 Updated documentation files: {', '.join(updated_files)}")
    else:
        print("\n📚 No documentation version references found to update")

    # Update __init__.py
    update_init_py(repo_root, version)

    print(f"\n🎉 Version update complete: {old_version} → {version}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <new_version>")
        sys.exit(1)

    new_version = sys.argv[1]
    update_version(new_version)
