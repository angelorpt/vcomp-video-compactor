<div align="center">
  <h1>vcomp</h1>
  <p><strong>Video Compactor — Compress video with ffmpeg + libx265</strong></p>

  <!-- Badges -->
  <p>
    <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+">
    <img src="https://img.shields.io/badge/ffmpeg-libx265-green?logo=ffmpeg&logoColor=white" alt="ffmpeg + libx265">
    <img src="https://img.shields.io/badge/Typer-0.12+-blueviolet" alt="Typer">
    <img src="https://img.shields.io/badge/Rich-13.0+-orange" alt="Rich">
    <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License MIT">
  </p>
</div>

---

## Motivation

You have a large collection of video eating up disk space. Re-encoding every file manually with ffmpeg is tedious, error-prone, and slow.

**vcomp** automates the whole process: point it at a directory, choose your output strategy, and let parallel compression do the heavy lifting — all with a beautiful terminal UI.

## Features

- **4 output modes**: same directory, backup originals, delete originals, or replicate to a separate directory
- **Recursive or flat scanning**: opt-in subdirectory traversal (`--recursive`)
- **Parallel compression**: uses all your CPU cores by default (`--jobs`)
- **Rich terminal UI**: live progress bars with ETA, color-coded summary table with space saved
- **Dry-run mode**: preview what would be compressed before committing
- **Overwrite protection**: skips existing files unless `--overwrite` is set
- **Rollback safety**: originals are only moved or deleted after successful compression
- **Backup cleanup**: `vcomp clean` finds and removes `.originais/` backup directories
- **Self-install**: `vcomp install` or `install.sh` to make it available system-wide
- **Configurable quality**: CRF, x265 preset, audio bitrate, file extensions

## Requirements

- **ffmpeg** built with `--enable-libx265` (check: `ffmpeg -version | grep libx265`)
- **Python 3.10+**
- Packages: `typer>=0.12`, `rich>=13.0` (installed automatically)

## Installation

### Option 1: pip install (recommended)

```bash
git clone https://github.com/anomalyco/video-compactor.git
cd video-compactor
python3 -m pip install --user -e .
vcomp --help
```

### Option 2: install.sh

```bash
git clone https://github.com/anomalyco/video-compactor.git
cd video-compactor
chmod +x install.sh
./install.sh
```

### Option 3: vcomp install

After installing via pip, you can also use the built-in install command:

```bash
vcomp install          # re-installs via pip
vcomp install --home   # copies a wrapper to ~/.local/bin/vcomp
```

## Quick Start

```bash
# Compress everything in ./videos (non-recursive, save next to originals)
vcomp run ./videos

# Compress recursively, move originals to .originais/ as backup
vcomp run ./videos --recursive --mode backup

# Preview what would happen
vcomp run ./videos --recursive --mode delete --dry-run

# Compress and replicate directory structure to another drive
vcomp run ./videos --recursive --mode separate --output-dir /mnt/backup/compactados

# Clean up all .originais/ directories
vcomp clean ./videos --recursive
```

## Output Modes

| Mode | Flag | Output File | Original File | Use Case |
|------|------|-------------|---------------|----------|
| **Same** | `--mode same` | `<name>_compactado.<ext>` | Unchanged | Safe start — manual review before cleanup |
| **Backup** | `--mode backup` | `<name>_compactado.<ext>` | Moved to `.originais/` | Keep originals but out of the way |
| **Delete** | `--mode delete` | `<name>_compactado.<ext>` | Deleted | Reclaim space immediately |
| **Separate** | `--mode separate -o <dir>` | `<dir>/<path>/<name>.<ext>` | Unchanged | Keep originals + compacted copies apart |

## Usage

### `vcomp run <directory>`

```
Arguments:
  directory                 Directory containing video files

Options:
  -r, --recursive           Scan subdirectories recursively
  -m, --mode <mode>         Output mode: same, backup, delete, separate
  -o, --output-dir <path>   Output directory (required for separate mode)
  --crf <int>               CRF value for x265 (0-51)  [default: 28]
  --preset <text>           x265 preset: ultrafast, fast, medium, slow, veryslow
  --audio-bitrate <text>    Audio bitrate  [default: 128k]
  --extensions <text>       Comma-separated extensions  [default: .mp4,.mov,.avi,.mkv,.webm,.m4v]
  -j, --jobs <int>          Number of parallel jobs  [default: CPU count]
  --overwrite               Re-compress existing files
  --dry-run                 Preview without compressing
```

### `vcomp clean [directory]`

```
Arguments:
  directory                 Directory to clean backups from  [default: .]

Options:
  -r, --recursive           Find .originais/ recursively
  --dry-run                 Show what would be deleted without deleting
```

### `vcomp install`

```
Options:
  --home, -H                Install to ~/.local/bin instead of pip
```

## Compression Quality

The default settings (`--crf 28 --preset medium --audio-bitrate 128k`) target a good balance between file size and quality for educational video content (talking heads, slides, screencasts).

| Content Type | Recommended CRF | Preset | Notes |
|-------------|----------------|--------|-------|
| Video courses / screencasts | 28 | medium | Good quality, ~40-60% size reduction |
| Movies / high-action | 24 | slow | Higher quality, less compression |
| Archival / maximum quality | 20 | veryslow | Minimal quality loss, much larger files |
| Maximum compression | 32 | ultrafast | Noticeable quality loss, smallest files |

**CRF scale** (Constant Rate Factor):
- 0–18: visually lossless / very high quality
- 19–24: high quality (good for movies)
- 25–30: good quality (excellent for courses)
- 31–40: low quality (small files)
- 51: worst quality

**Presets** control encoding speed vs compression efficiency:
- `ultrafast` / `fast`: quick but larger files
- `medium`: balanced (default)
- `slow` / `veryslow`: slower but smaller files at same quality

## Architecture

```
vcomp run ./videos
  │
  ├── scanner.py              os.walk / os.scandir → list of VideoFile
  ├── path_resolver.py        Shared output path logic (DRY)
  ├── ffmpeg_service.py       ffmpeg command builder + executor
  ├── prerequisite_checker.py ffmpeg + Python deps verification
  ├── compressor.py           ProcessPoolExecutor orchestration
  ├── interfaces.py           Protocol classes (Dependency Inversion)
  ├── models.py               Data classes: VideoFile, CompressionTask, etc.
  └── cli.py                  Typer CLI + Rich Progress / Table
```

Built with **Python** using:
- [**Typer**](https://typer.tiangolo.com/) — CLI argument parsing and subcommands
- [**Rich**](https://rich.readthedocs.io/) — Terminal UI (progress bars, tables, colors)
- **ffmpeg** with libx265 (HEVC) — Video encoding
- **SOLID principles**: single-responsibility modules, protocol-based DI, no code duplication

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest -v

# With coverage report
pytest --cov=vcomp --cov-report=term-missing

# Run only unit tests (fast, no CLI subprocess)
pytest tests/ -k "not integration" -v

# Run only integration tests (requires ffmpeg)
pytest tests/test_integration.py -v
```

Tests use a mock ffmpeg script (no real encoding needed). 43 tests covering path logic, scanner, compressor, CLI, models, and end-to-end flows.

## Project Status

**Version 1.0.0** — Core functionality implemented. SOLID refactored with test suite.

Planned:
- Progress ETA per individual file
- Resume interrupted compressions
- Config file support

## License

[MIT](LICENSE)
