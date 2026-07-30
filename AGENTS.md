# vcomp — AGENTS.md

## Project

CLI tool `vcomp` to compress video files with ffmpeg + libx265. Built with Python (Typer + Rich), planned via OpenSpec.

## Entry point

`vcomp.cli:app` — a `typer.Typer()` app. Registered as console script in `pyproject.toml:project.scripts`. Also runnable via `python -m vcomp`.

## Key commands

```bash
pip install -e .            # install dev (needs .venv on Ubuntu — externally managed env)
vcomp run <dir>             # compress videos
vcomp clean [dir]           # remove .originais/ backups
vcomp install --home        # install to ~/.local/bin/vcomp
```

## Package discovery quirk

`pyproject.toml` **must** include `[tool.setuptools.packages.find] include = ["vcomp*"]` — without it, setuptools fails with "Multiple top-level packages" because `openspec/` shares the root.

## Architecture

- `cli.py` — Typer commands, Rich UI, prerequisite check
- `scanner.py` — `os.walk` or `os.scandir`; default extensions `.mp4,.mov,.avi,.mkv,.webm,.m4v`
- `compressor.py` — `ProcessPoolExecutor` calling subprocess ffmpeg; output path logic duplicated in both `cli.py` and `compressor.py` (dry-run vs actual)
- `models.py` — `OutputMode` enum, `VideoFile`, `CompressionResult`, `CompressionReport`

## Parallelism caveat

`_compress_single` runs in a `ProcessPoolExecutor`. Its `args` tuple **must** be picklable — no closures, no lambdas, only plain types (`VideoFile`, `Path`, `str`, `int`, `OutputMode`).

## Required system dep

ffmpeg built with `--enable-libx265`. Checked at runtime via `ffmpeg -version | grep libx265`.

## OpenSpec workflow

Changes are managed under `openspec/changes/`. Commands via `.opencode/commands/`:
- `/opsx-propose <name>` — create change + all artifacts in one step
- `/opsx-apply` — implement from tasks

## Testing

No test suite exists yet.
