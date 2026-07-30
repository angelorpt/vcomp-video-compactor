## Why

Output modes and naming conventions mix Portuguese and English, use confusing semantics, and require manual post-processing (renaming `_compactado` files). The backup directory name `.originais` is Portuguese. The flow lacks logging, resume, and rollback capabilities, making it hard to recover from failures or verify results.

## What Changes

**BREAKING** — All mode names changed, `backup` mode removed, output paths changed, backup directory renamed, log format introduced.

- Rename modes: `same` → `keep`, `delete` → `replace`, `separate` → `clone`
- Remove `backup` mode (replaced by the new standard flow)
- Eliminate `_compactado` suffix: compressed file takes the original name in-place
- Rename `.originais/` → `_originals/`
- All modes (except `clone`): move original to `_originals/` before compression
- `replace`: auto-delete original from `_originals/` per-file on success; remove `_originals/` if empty
- `keep`: preserve `_originals/`; user runs `clean` later
- JSON log per directory (`vcomp-log.json`) recording per-file status + session state
- Resume: re-run picks up from `_originals/`, reprocesses only failed/interrupted files
- `clean`: removes `_originals/` directories
- `clean --logs`: removes only `vcomp-log.json` files
- New command `rollback`: restores originals from `_originals/`, deletes compressed files, cleans up

## Capabilities

### Modified Capabilities
- `output-modes`: all four modes renamed/removed, new behavior for originals flow, resume, and logging
- `backup-cleanup`: target directory changed to `_originals/`, `--logs` flag added, new `rollback` command

## Impact

- `vcomp/models.py`: update `OutputMode` enum (rename values, remove `BACKUP`)
- `vcomp/path_resolver.py`: remove `_compactado` suffix, adapt for new modes
- `vcomp/ffmpeg_service.py`: move original to `_originals/` pre-compression, handle `replace` vs `keep` post-compression
- `vcomp/compressor.py`: resume logic, logging integration
- `vcomp/cli.py`: update mode options, add `rollback` command, `clean --logs`
- `vcomp/scanner.py`: no changes expected
- `tests/`: update all tests for new mode names, paths, and behavior
- `README.md`: rewrite mode explanation section
