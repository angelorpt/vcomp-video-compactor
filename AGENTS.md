# vcomp

CLI tool to compress videos with ffmpeg + libx265. Python, Typer, Rich.

## Entry point

`vcomp.cli:app` — `typer.Typer()`. Console script in `pyproject.toml:project.scripts`. Also `python -m vcomp`.

## Commands

```bash
pip install -e ".[dev]"     # install with test deps (.venv on Ubuntu)
pytest -v                    # 43 tests (unit + integration with mock ffmpeg)
pytest --cov=vcomp --cov-report=term-missing
vcomp run <dir>              # compress videos
vcomp clean [dir]            # remove .originais/ backups
vcomp install --home         # install to ~/.local/bin/vcomp
```

## Structure

```
vcomp/
  cli.py              CLI + Rich UI (delegates to services)
  compressor.py       ProcessPoolExecutor orchestration
  ffmpeg_service.py   ffmpeg command builder + executor
  interfaces.py       Protocol classes (FFmpegExecutor, PathResolver, PrerequisiteChecker)
  models.py           Data classes (VideoFile, CompressionTask, CompressionResult, CompressionReport)
  path_resolver.py    Shared output path logic
  prerequisite_checker.py  ffmpeg + Python deps verification
  scanner.py          Directory scan
tests/
  test_*.py           pytest suite, mock ffmpeg in conftest.py
```

## Package quirk

`pyproject.toml` must have `[tool.setuptools.packages.find] include = ["vcomp*"]` — without it, setuptools fails with "Multiple top-level packages" because `openspec/` shares the root.

## Parallelism caveat

`_compress_single` runs in `ProcessPoolExecutor`. Task args use `CompressionTask` dataclass (plain types only — picklable). No closures or lambdas in worker args.

## Required system dep

ffmpeg with `--enable-libx265`. Checked at runtime: `ffmpeg -version | grep libx265`.

## OpenSpec workflow

Changes under `openspec/changes/`. Commands via `.opencode/commands/`:
- `/opsx-propose <name>` — create change + all artifacts
- `/opsx-apply` — implement from tasks
