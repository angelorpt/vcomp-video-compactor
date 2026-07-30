## Why

The codebase has functional gaps: duplicated output path logic (cli.py + compressor.py), CLI with too many responsibilities, mutable state mixed with progress display, and no test suite. Without tests, regressions go undetected and refactoring becomes risky.

## What Changes

- Extract `_build_output_path` into a single shared function in a dedicated module
- Introduce service/repository layers to separate CLI (UI) from business logic
- Make `CompressionReport` immutable and decouple from progress callbacks
- Replace raw tuple args in `_compress_single` with a typed dataclass
- Extract ffmpeg command builder into its own service
- Add comprehensive test suite with pytest (unit + integration via ffmpeg dry-run)
- No behavior changes — output paths, CLI flags, ffmpeg arguments remain identical

## Capabilities

Pure refactoring and test infrastructure — no spec-level behavior changes. `skip_specs: true` set in `.openspec.yaml`.

## Impact

- `vcomp/` restructured internally — public CLI API (`vcomp run`, `vcomp clean`, `vcomp install`) unchanged
- New dependencies: `pytest`, `pytest-cov` (dev only)
- ffmpeg still required for integration tests; unit tests mock subprocess calls
