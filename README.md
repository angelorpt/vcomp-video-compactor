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

- **3 output modes**: keep (preserve originals in `_originals/`), replace (auto-cleanup originals on success), clone (mirror to separate directory)
- **In-place compression**: no `_compactado` suffix — compressed file replaces the original at the same path
- **Pre-compression backup**: originals are safely moved to `_originals/` before encoding (enables resume + rollback)
- **Recursive or flat scanning**: opt-in subdirectory traversal (`--recursive`)
- **Parallel compression**: uses all your CPU cores by default (`--jobs`)
- **Rich terminal UI**: live progress bars with ETA, color-coded summary table with space saved
- **Dry-run mode**: preview what would be compressed before committing
- **Overwrite protection**: skips existing files unless `--overwrite` is set
- **Resume interrupted sessions**: re-run detects `_originals/` and resumes from where it left off
- **JSON session logging**: per-file status logged to `vcomp-log.json` at the processed root
- **Backup cleanup**: `vcomp clean` removes `_originals/` directories
- **Log cleanup**: `vcomp clean --logs` removes only log files
- **Rollback**: `vcomp rollback` restores originals from `_originals/`
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
# Compress everything in ./videos (keep originals in _originals/)
vcomp run ./videos

# Compress and auto-delete originals on success
vcomp run ./videos --mode replace

# Preview what would happen
vcomp run ./videos --dry-run

# Compress and replicate directory structure to another drive
vcomp run ./videos --mode clone --output-dir /mnt/backup/compactados

# Clean up all _originals/ directories
vcomp clean ./videos --recursive

# Remove only log files
vcomp clean ./videos --logs

# Rollback: restore originals and remove compressed files
vcomp rollback ./videos
```

## Output Modes

| Mode | Flag | Output File | Original File | Use Case |
|------|------|-------------|---------------|----------|
| **Keep** (default) | `--mode keep` | `<name>.<ext>` (in-place) | Moved to `_originals/` | Safe — manual cleanup later |
| **Replace** | `--mode replace` | `<name>.<ext>` (in-place) | Moved to `_originals/`, auto-deleted on success | Reclaim space immediately |
| **Clone** | `--mode clone -o <dir>` | `<dir>/<path>/<name>.<ext>` | Unchanged | Keep originals + compressed copies apart |

### How the originals flow works

1. Before compression, the original is moved to `<parent>/_originals/<filename>`
2. Compression writes the output directly to the original path (in-place)
3. After successful compression:
   - **keep**: originals remain in `_originals/` — run `vcomp clean` to purge
   - **replace**: each original is deleted from `_originals/` immediately; empty `_originals/` is removed
   - **clone**: originals stay put (no move)

This pre-compression move is the key design decision — it prevents data loss if compression is interrupted and enables both resume and rollback.

## Usage

### `vcomp run <directory>`

```
Arguments:
  directory                 Directory containing video files

Options:
  -r, --recursive           Scan subdirectories recursively
  -m, --mode <mode>         Output mode: keep (default), replace, clone
  -o, --output-dir <path>   Output directory (required for clone mode)
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
  directory                 Directory to clean  [default: .]

Options:
  -r, --recursive           Find _originals/ recursively
  -l, --logs                Remove only vcomp-log.json files
  --dry-run                 Show what would be deleted without deleting
```

### `vcomp rollback [directory]`

Restores originals from `_originals/` directories, overwriting compressed files. Removes `_originals/` and `vcomp-log.json` after restoration.

```
Arguments:
  directory                 Directory to rollback  [default: .]

Options:
  --dry-run                 Show what would be restored without executing
```

### `vcomp install`

```
Options:
  --home, -H                Install to ~/.local/bin instead of pip
```

## JSON Session Log

Each `vcomp run` session writes a `vcomp-log.json` file at the processed root directory:

```json
{
  "session": "completed",
  "files": [
    {
      "file": "/path/to/video.mp4",
      "status": "completed",
      "input_size": 1000000,
      "output_size": 500000,
      "error": null,
      "timestamp": "2026-07-30T12:00:00+00:00"
    }
  ]
}
```

- `session`: `"completed"` when all files finish; `"interrupted"` if the user hits Ctrl+C
- `status`: `"completed"`, `"failed"`, or `"skipped"`
- Written atomically (temp file + rename) to prevent corruption

## Resume Behavior

If a session is interrupted (Ctrl+C), re-run the same command:

1. vcomp detects `_originals/` with files from the interrupted session
2. Only files in `_originals/` are processed (files that completed are skipped)
3. Running `vcomp run` again resumes where you left off

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
  ├── ffmpeg_service.py       ffmpeg command builder + executor (handles originals move)
  ├── logger.py               CompressionLogger — JSON session logging
  ├── prerequisite_checker.py ffmpeg + Python deps verification
  ├── compressor.py           ProcessPoolExecutor orchestration + resume detection
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

Tests use a mock ffmpeg script (no real encoding needed). Tests cover path logic, scanner, compressor, CLI, models, logging, and end-to-end flows.

## Project Status

**Version 2.0.0** — Modes redesigned, in-place compression, pre-compression originals flow, JSON logging, resume, rollback.

## License

[MIT](LICENSE)
