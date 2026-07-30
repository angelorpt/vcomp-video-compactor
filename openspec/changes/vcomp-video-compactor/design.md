# Design

## Architecture

```
vcomp/                  # Python package
├── __init__.py         # Package init, version
├── __main__.py         # python -m vcomp entry point
├── cli.py              # Typer CLI (run, clean, install)
├── scanner.py          # Directory scanning + ffmpeg input validation
├── compressor.py       # ffmpeg subprocess + parallel execution
└── models.py           # Data classes (OutputMode, CompressionResult)

pyproject.toml          # Package config, dependencies, entry point
install.sh              # Alternative install script
```

## Data Flow

1. `cli.py` parses args → calls `scanner.py`
2. `scanner.py` walks directory → returns list of `VideoFile` objects
3. `cli.py` passes video list + options to `compressor.py`
4. `compressor.py` runs ffmpeg in parallel via `ProcessPoolExecutor`
5. Progress reported via `rich.progress.Progress`
6. Summary table rendered via `rich.table.Table`

## CLI Design

```
vcomp run <dir>         # default subcommand
vcomp clean [dir]
vcomp install
```

Using Typer subcommands for clean separation. `run` is the default.

## Output Modes

| Mode | Output Location | Original File |
|------|----------------|---------------|
| `same` | `<name>_compactado.<ext>` | Unchanged |
| `backup` | `<name>_compactado.<ext>` | Moved to `.originais/` |
| `delete` | `<name>_compactado.<ext>` | Deleted |
| `separate` | `<output-dir>/<path>/<name>.<ext>` | Unchanged |

## Error Handling

- ffmpeg failures tracked per-file; errors collected and reported in summary
- No partial state: backup/delete modes only act after successful compression
- KeyboardInterrupt handled gracefully — running jobs finish, completed ones reported

## Dependencies

- `typer>=0.12` — CLI framework
- `rich>=13.0` — Terminal UI (progress, tables, colors)
- `ffmpeg` (system dep) — Video encoding
