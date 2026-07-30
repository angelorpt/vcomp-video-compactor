# Tasks

## Checklist

- [x] Create project scaffold (`pyproject.toml`, `vcomp/` package structure)
- [x] Implement data models (`models.py`: OutputMode enum, CompressionResult, VideoFile)
- [x] Implement directory scanner (`scanner.py`: walk dirs, filter extensions)
- [x] Implement compression engine (`compressor.py`: ffmpeg subprocess, parallel pool)
- [x] Implement CLI with Typer (`cli.py`: run, clean, install subcommands)
- [x] Install `typer>=0.12` and `rich>=13.0` dependencies
- [x] Verify syntax and structure — all commands tested: `run --dry-run`, `run` (compress), `run --mode backup` (backup + move), `run --mode delete`, `clean --dry-run`, `clean` (delete), `install --help`
