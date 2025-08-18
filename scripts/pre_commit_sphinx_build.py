#!/usr/bin/env python3
"""Pre-commit hook for building Sphinx documentation."""

import subprocess  # nosec B404
import sys


def main() -> int:
    """Build Sphinx documentation."""
    try:
        # First, ensure docs dependencies are installed
        subprocess.run(  # nosec B603, B607
            [
                "uv",
                "sync",
                "--group",
                "docs",
            ],
            check=True,
        )

        # Then build the documentation
        subprocess.run(  # nosec B603, B607
            [
                "uv",
                "run",
                "--group",
                "docs",
                "sphinx-build",
                "-b",
                "html",
                "docs",
                "docs/_build/html",
                "-W",
                "--keep-going",
            ],
            check=True,
        )
        print("✅ Sphinx documentation built successfully")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Sphinx build failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
