# Image Converter

Desktop application to convert images to WebP and AVIF formats with automatic resizing.

## Features

- Drag & drop folder or single file
- Output formats: WebP, AVIF, or both
- 5 resolutions per image: original, large, medium, small, x-small
- Configurable quality (0-100%)
- Parallel threading for fast processing
- Export/Import configurations
- Skip existing files option

## Installation

### Dependencies

```bash
pip install -r requirements.txt
```

### Build executable

```bash
./build.sh
```

## Usage

Run with Python:
```bash
./venv/bin/python main.py
```

Or use the built executable:
```bash
./dist/ImageConverter
```

## Options

### Output Options
- **Output folder**: Custom output location
- **Prefix**: Add prefix to filenames
- **Overwrite**: Replace existing files
- **Skip**: Skip already converted files

### Resize Options
- Large: 1200px (default)
- Medium: 800px (default)
- Small: 400px (default)
- X-Small: 200px (default)

### Resize Method
- LANCZOS (default)
- BICUBIC
- BILINEAR
- NEAREST

## Input Formats

PNG, JPG, JPEG, BMP, TIFF, TIF, WEBP, AVIF, GIF, HEIC, HEIF

## Tech Stack

- Python 3.12
- Tkinter + tkinterdnd2
- Pillow + pillow-avif-plugin
- PyInstaller

## Build for Windows

Use GitHub Actions workflow:
- Go to Actions > Build Windows > Run workflow

Or build manually on Windows:
```powershell
pip install -r requirements.txt pyinstaller
.\build.ps1
```

## Configuration

User settings saved in: `~/.imgconverter/config.json`

Export/Import via GUI buttons or use config JSON files.

## License

MIT