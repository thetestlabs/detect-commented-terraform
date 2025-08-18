# API Reference

This page provides detailed documentation for the public API of `detect-commented-terraform`.

## Core Classes

### TerraformCommentDetector

```{eval-rst}
.. autoclass:: detect_commented_terraform.TerraformCommentDetector
   :members:
   :show-inheritance:
```

### CommentedCodeBlock

```{eval-rst}
.. autoclass:: detect_commented_terraform.CommentedCodeBlock
   :members:
   :show-inheritance:
```

### DetectionResult

```{eval-rst}
.. autoclass:: detect_commented_terraform.models.DetectionResult
   :members:
   :show-inheritance:
```

## Usage Examples

### Basic Detection

```python
from detect_commented_terraform import TerraformCommentDetector
from pathlib import Path

# Create detector instance
detector = TerraformCommentDetector(root_path=Path("."))

# Scan a directory
result = detector.scan_directory(Path("./terraform"))

# Check results
if result.has_commented_code:
    print(f"Found {result.total_blocks} commented code blocks")
    for block in result.blocks:
        print(f"  {block.relative_path}:{block.line_range}")
```

### Programmatic File Processing

```python
from detect_commented_terraform import TerraformCommentDetector
from pathlib import Path

detector = TerraformCommentDetector()

# Scan a single file
blocks = list(detector.scan_file(Path("main.tf")))

for block in blocks:
    print(f"File: {block.file_path}")
    print(f"Lines: {block.line_range}")
    print(f"Content: {block.first_line.strip()}")
```
