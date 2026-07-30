## Context

Current code has 4 modules (cli.py, compressor.py, scanner.py, models.py). Key issues: `_build_output_path` duplicated in cli.py and compressor.py, cli.py mixes CLI/UI/business logic/clean/install, `_compress_single` uses fragile tuple args, `CompressionReport` is mutable and mutated via callback side-effect, no tests. See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- Single Responsibility: each module has one concern
- Dependency Inversion: CLI depends on abstractions, not concrete ffmpeg calls
- Extract shared `_build_output_path` into reusable path resolver
- Replace raw tuple with typed dataclass for worker args
- Make report accumulation explicit (not callback side-effect)
- Add pytest suite with unit tests (mocked ffmpeg) + integration tests (real ffmpeg dry-run)
- Achieve >80% line coverage

**Non-Goals:**
- No CLI flag or behavior changes
- No ffmpeg argument changes
- No new features

## Decisions

1. **Protocol classes over ABC** — Use `typing.Protocol` for interfaces (e.g., `FFmpegExecutor`, `PathResolver`). Lighter than ABC, idiomatic Python duck typing. Alternatives considered: ABC (too heavy), no interfaces (defeats DIP).

2. **`ProcessPoolExecutor` stays, args via dataclass** — Replace raw 6-tuple with `CompressionTask` dataclass. Must be picklable (flat dataclass, no methods beyond `__init__`). Alternatives: `multiprocessing` (same constraint), `threading` (GIL-bound for subprocess).

3. **Output path logic shared via `path_resolver.py`** — Extract `_build_output_path` into single module used by both CLI (dry-run) and compressor (actual). Current duplicate is the clearest DRY violation.

4. **Report as accumulator, not callback mutation** — `compress_videos` returns results list; caller (CLI) builds report from it. Progress callback remains for UI but only for display, not state.

5. **`PrerequisiteChecker` as explicit dependency** — Extract `check_ffmpeg` + Python deps check into injectable checker. Makes it mockable for tests.

6. **pytest with `tmp_path` fixture for integration tests** — Create temp video files, mock ffmpeg with a script that just copies input to output (tests path logic, parallelism, error handling).

## Risks / Trade-offs

- [Risk] ProcessPoolExecutor pickling constraints limit how we structure args → Mitigation: `CompressionTask` is a flat dataclass of plain types only
- [Risk] Integration tests require ffmpeg on CI → Mitigation: mark with `@pytest.mark.integration`, skip if ffmpeg not found; unit tests cover all logic paths
- [Trade-off] Protocol classes add indirection → Worth it: enables mock injection without monkey-patching
