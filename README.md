# Image Processor

Processes images by creating a blurred background and overlaying a thumbnail with optional text from a companion `.txt` file.

## Features

- Resizes original images to create a blurred 1920px background
- Places a 500px thumbnail at position (300, 200)
- Renders text from matching `.txt` file with Roboto 13pt font at position (700, 200)
- Outputs as PSD file with original image name
- Dry-run mode for testing without creating files

## Usage

```bash
make run       # Process images
make dry-run   # Test without creating files
make lint      # Run linter
make fix       # Auto-fix lint issues
```

## Requirements

- Python 3.13+
- psd-tools
- Pillow
