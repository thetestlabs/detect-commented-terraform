#!/usr/bin/env python3
"""
Pre-commit hook: Detect commented-out Terraform code in .tf files.
Blocks commits if commented lines look like Terraform code (resources, variables, assignments, etc).
"""

import re
import sys
import subprocess
from pathlib import Path

# Terraform keywords and common property patterns
KEYWORDS = r"(resource|variable|output|module|provider|data|locals|terraform)"
PROPERTY_PATTERN = r"(\s*#.*\b\w+\s*=\s*.+|\s*#.*[{}])"


def is_commented_terraform(line):
    """
    Return True if the line is a commented-out Terraform code line.
    Matches lines that start with #, //, or /* and contain a Terraform keyword or property pattern.
    """
    return re.match(r"^\s*(#|//|/\*).*\b" + KEYWORDS + r"\b", line) or re.match(
        PROPERTY_PATTERN, line
    )


def main():
    """
    Main entry point: scan staged .tf files for commented-out Terraform code and block commit if found.
    """
    # Get staged .tf files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        check=False,
    )
    files = [f for f in result.stdout.splitlines() if f.endswith(".tf") and Path(f).is_file()]
    found = False

    for file in files:
        with open(file, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                if is_commented_terraform(line):
                    print(
                        f"{file}:{lineno}: Commented-out Terraform code detected:\n  {line.rstrip()}"
                    )
                    found = True

    if found:
        print("❌ Commit aborted: Please remove commented-out Terraform code.")
        sys.exit(1)


if __name__ == "__main__":
    main()
