## Why

Large collection of video courses consuming excessive disk space. Manual re-encoding with ffmpeg is tedious and error-prone. An automated CLI tool with sensible defaults, parallel processing, pretty terminal output, and flexible output modes will save time and space while keeping adequate quality for educational content.

## What Changes

- Created `vcomp` — a Python CLI tool that scans directories for video files and compresses them using ffmpeg with libx265
- Supports 4 output modes: same-directory, backup (move originals to `.originais/`), delete originals after compression, and separate output directory (replicated structure)
- `clean` subcommand to purge backup directories found via `vcomp clean [dir]`
- `install` subcommand (`--home` or pip-based) to make the tool available system-wide
- Parallel compression via `ProcessPoolExecutor` with `--jobs` flag
- Terminal UI: `rich.Progress` with ETA + `rich.Table` summary (sizes, ratio, errors)
- Prerequisites checked at runtime (ffmpeg + libx265, Python deps)

## Capabilities

### New Capabilities

- `compress-videos`: Directory scanning (recursive or flat), file extension filtering, parallel ffmpeg execution via `ProcessPoolExecutor`, live progress bar, and a compression summary table with space saved breakdown.
- `output-modes`: Four modes implemented — `same` (`_compactado` suffix), `backup` (originals moved to `.originais/`), `delete` (originals removed after success), `separate` (directory structure replicated to `--output-dir`). Skipped files tracked independently. Rollback safety: originals only moved/deleted after successful compression.
- `backup-cleanup`: `vcomp clean [dir]` scans for `.originais/` directories (recursively), shows total size, asks confirmation, deletes. Dry-run mode available.
- `install-command`: `vcomp install --home` installs to `~/.local/bin/vcomp`; without `--home` uses `pip install --user -e .`. `install.sh` script also provided for dependency-first workflow.

### Modified Capabilities

## Impact

- New Python package with 2 external dependencies: `typer>=0.12` and `rich>=13.0`
- Requires `ffmpeg` with `libx265` support (checked at runtime)
- New command `vcomp` available via venv; `install` command or `pip install` for system-wide use
- No impact on existing project files
