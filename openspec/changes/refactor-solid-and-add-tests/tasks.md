## 1. Setup & Infrastructure

- [x] 1.1 Add `pytest` and `pytest-cov` to pyproject.toml dev dependencies
- [x] 1.2 Create `tests/` directory with `__init__.py` and `conftest.py`
- [x] 1.3 Create mock ffmpeg script for integration tests

## 2. Path Resolver Extraction

- [x] 2.1 Create `vcomp/path_resolver.py` with shared `build_output_path` function
- [x] 2.2 Replace duplicated `_build_output_path` in cli.py and compressor.py with import

## 3. Protocol Interfaces

- [x] 3.1 Create `vcomp/interfaces.py` with `FFmpegExecutor`, `PathResolver`, `PrerequisiteChecker` protocols

## 4. FFmpeg Service

- [x] 4.1 Create `vcomp/ffmpeg_service.py` with `FFmpegCommandBuilder` (build ffmpeg cmd) and `FFmpegProcessExecutor` (run subprocess)
- [x] 4.2 Create `CompressionTask` dataclass for worker args

## 5. Prerequisite Checker

- [x] 5.1 Create `vcomp/prerequisite_checker.py` with `SystemPrerequisiteChecker` (ffmpeg + Python deps)

## 6. Compressor Refactor

- [x] 6.1 Refactor `compress_videos` to accept `FFmpegExecutor` protocol (DI)
- [x] 6.2 Replace raw tuple in `_compress_single` with `CompressionTask` dataclass
- [x] 6.3 Remove output path building from compressor (now uses path_resolver)

## 7. CLI Refactor

- [x] 7.1 Extract progress display and report building from CLI to dedicated functions
- [x] 7.2 Inject services (PrerequisiteChecker, FFmpegExecutor) into CLI
- [x] 7.3 Remove duplicate `_build_output_path` and `_format_size` from cli.py

## 8. Unit Tests

- [x] 8.1 Test `path_resolver.py` — all output modes, edge cases
- [x] 8.2 Test `scanner.py` — recursive, non-recursive, empty dir, extensions filter
- [x] 8.3 Test `ffmpeg_service.py` — command building args, executor mock
- [x] 8.4 Test `prerequisite_checker.py` — ffmpeg found/missing, deps found/missing
- [x] 8.5 Test `compressor.py` — success, skip, error, all output modes, parallelism
- [x] 8.6 Test `models.py` — `CompressionReport`, `CompressionResult` properties

## 9. Integration Tests

- [x] 9.1 Test end-to-end with mock ffmpeg: run command, verify output paths
- [x] 9.2 Test clean command with .originais/ directories
- [x] 9.3 Test dry-run mode produces correct table data

## 10. Final Verification

- [x] 10.1 Run full test suite, confirm all tests pass
- [x] 10.2 Run `python -m vcomp --help` to confirm CLI still works
