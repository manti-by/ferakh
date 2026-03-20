# Agent Instructions

## Project Overview

Image processing tool that creates PSD files with blurred backgrounds, thumbnails, and optional text overlays.

## Build/Lint/Test Commands

```bash
# Install dependencies
uv sync

# Run the script
make run

# Dry run (no file creation)
make dry-run

# Lint with ruff
make lint

# Auto-fix lint issues
make fix

# Clean log file
make clean
```

### Manual Commands

```bash
uv run python main.py [--dry-run]
uv run ruff check .
uv run ruff check --fix .
```

## Code Style Guidelines

### General

- 4-space indentation (standard Python)
- Single quotes for strings (`'text'` not `"text"`)
- Trailing commas in multi-line structures
- Max line length: 88 characters (ruff default)
- Type annotations required for function signatures

### Imports

Order: stdlib → third-party → local

```python
import argparse
import logging
import logging.config
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from psd_tools import PSDImage
```

### Naming Conventions

- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Variables: `snake_case`
- Modules: `snake_case`

### Type Hints

Use modern syntax where possible:

```python
def func(a: str, b: int) -> bool | None:
    ...
```

### Logging

- Use module-level logger: `logger = logging.getLogger(__name__)`
- Logging config via dictConfig at module level
- Log levels: INFO for actions, WARNING for issues, ERROR for failures
- No print statements; use logging only

### Error Handling

- Catch specific exceptions: `except (OSError, IOError):`
- Fallback gracefully (e.g., load default font if custom fails)
- Dry-run mode must not raise errors

### Testing

- Test files should be minimal (manual testing via `make dry-run`)
- Verify no lint errors before completing tasks

## File Structure

```
.
├── main.py           # Main script
├── Makefile          # Build commands
├── pyproject.toml    # Dependencies
├── README.md         # Project docs
└── AGENTS.md         # This file
```

## Dependencies

- Python 3.13+
- `psd-tools` - PSD file manipulation
- `Pillow` - Image processing
- `ruff` - Linting (dev)

## Key Implementation Notes

- PSD creation uses `PSDImage.new()` with `mode="RGBA"` and integer dimensions
- Blur radius: 15 pixels
- Background resize: 1920px shortest dimension
- Thumbnail resize: 500px shortest dimension
- Thumbnail position: (300, 200)
- Text position: (700, 200)
- Text font: Roboto 13pt (fallback to default if unavailable)
