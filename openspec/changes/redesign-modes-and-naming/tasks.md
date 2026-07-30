## 0. Prerequisite

- [ ] 0.1 Run existing test suite (`pytest -v`) — all tests pass before any changes
- [ ] 0.2 Read current `README.md` and `AGENTS.md` to know what to update

## 1. Models + Tests

- [x] 1.1 Update `OutputMode` enum: `SAME`→`KEEP`, `DELETE`→`REPLACE`, `SEPARATE`→`CLONE`, remove `BACKUP`
- [x] 1.2 Update `test_models.py` — enum values, remove BACKUP tests
- [x] 1.3 Confirm tests pass: `pytest tests/test_models.py -v`

## 2. Path Resolver + Tests

- [x] 2.1 Update `build_output_path` — `keep`/`replace` return original path directly (no suffix), `clone` uses `--output-dir` mirroring
- [x] 2.2 Update `test_path_resolver.py` — no suffix, new mode names
- [x] 2.3 Confirm tests pass: `pytest tests/test_path_resolver.py -v`

## 3. FFmpeg Service + Tests

- [x] 3.1 Move original to `<parent>/_originals/` at start of `execute_ffmpeg` (pre-compression)
- [x] 3.2 After successful compression: in `replace` mode, delete original from `_originals/`; in `keep` mode, leave it
- [x] 3.3 Adapt `output_path` creation to point at original location (in-place)
- [x] 3.4 Update `test_ffmpeg_service.py` — pre-compression move, post-compression cleanup per mode
- [x] 3.5 Confirm tests pass: `pytest tests/test_ffmpeg_service.py -v`

## 4. Logging Module + Tests

- [x] 4.1 Create `vcomp/logger.py` with `CompressionLogger` class — write/append JSON log at processed root
- [x] 4.2 Define JSON schema: per-file entries with `status` (completed/failed), sizes, error, timestamp + session field
- [x] 4.3 Add `test_logger.py` — JSON log format, append mode, atomic write
- [x] 4.4 Confirm tests pass: `pytest tests/test_logger.py -v`

## 5. Compressor + Tests

- [x] 5.1 Add resume detection — if `<input_dir>/_originals/` exists with files, use those as source
- [x] 5.2 Skip files already present at target path
- [x] 5.3 Integrate `CompressionLogger` — log after each file and on session end
- [x] 5.4 Update `test_compressor.py` — resume logic, logging
- [x] 5.5 Confirm tests pass: `pytest tests/test_compressor.py -v`

## 6. CLI + Tests

- [x] 6.1 Update `run` command: rename options to new mode names, update help text
- [x] 6.2 Update `clean` command: target `_originals/` instead of `.originais/`, add `--logs` / `-l` flag
- [x] 6.3 Add `rollback` command: restore originals, remove `_originals/` and logs (with `--dry-run`)
- [x] 6.4 Update CLI tests — new mode names, rollback, clean --logs
- [x] 6.5 Confirm tests pass: `pytest tests/test_integration.py -v`

## 7. Documentation

- [x] 7.1 Update README.md — detailed explanation of keep/replace/clone modes, `_originals/` workflow, JSON log format, rollback command, clean vs clean --logs, resume behavior
- [x] 7.2 Update AGENTS.md — new `vcomp/logger.py` module, updated module list

## 8. Final Verification

- [x] 8.1 Run full test suite (`pytest -v`) — all tests pass
- [ ] 8.2 Manual test: `vcomp run --mode keep dir/`, verify `_originals/` created and compressed in-place
- [ ] 8.3 Manual test: `vcomp run --mode replace dir/`, verify auto-cleanup of `_originals/`
- [ ] 8.4 Manual test: `vcomp rollback dir/`, verify originals restored
- [ ] 8.5 Manual test: `vcomp clean --logs dir/`, verify only logs removed
- [ ] 8.6 Manual test: interrupt with Ctrl+C, re-run, verify resume
