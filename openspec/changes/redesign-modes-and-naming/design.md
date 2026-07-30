## Context

Currently the compressor moves originals *after* compression (`BACKUP` moves to `.originais/`, `DELETE` deletes). The new flow moves originals to `_originals/` *before* compression. This enables resume and rollback. The output always replaces the original in-place (no suffix). See proposal.md for motivation and specs for full requirements.

## Goals / Non-Goals

**Goals:**
- Pre-compression move of originals to `_originals/`
- In-place compression (no `_compactado` suffix)
- JSON logging per directory
- Resume from `_originals/` on re-run
- New `rollback` command
- `clean --logs` flag

**Non-Goals:**
- No changes to `clone` mode output behavior
- No new external dependencies
- No changes to the parallel compression engine (ProcessPoolExecutor)

## Decisions

1. **Pre-compression move (ffmpeg_service.py)**: Move original to `_originals/` at the start of `execute_ffmpeg`, before running ffmpeg. If ffmpeg fails, the original is already safe in `_originals/`. Alternative: move in compressor.py before submitting task — rejected because each worker should self-contain the move for clarity.

2. **Log location**: One `vcomp-log.json` per directory root (the directory passed to `vcomp run`), not per subdirectory. But the user asked for one per subdirectory... re-reading: "Talvez seja melhor deixar um para cada diretorio, pois eu posso querer rodar um subdiretorio individualmente." — So log goes at the processed root (where `run` points). When you process a subdirectory individually, that subdirectory gets its own log.

3. **No suffix**: `build_output_path` for `keep`/`replace` returns the original path directly. The file system collision is avoided because the original was moved to `_originals/` first.

4. **Resume detection**: In `compress_videos`, check if `<input_dir>/_originals/` exists and has files. If so, use those as the source list instead of scanning the directory. Skip files that already exist at target path.

5. **Log schema**: JSON file with a top-level object `{ "session": "completed"|"interrupted", "files": [...] }`. Written atomically (write to temp, rename) to avoid corruption.

6. **`keep` vs `replace`**: Both move originals to `_originals/` pre-compression. Difference is post-compression cleanup:
   - `keep`: never removes `_originals/` content
   - `replace`: deletes each original from `_originals/` per-file on success; removes `_originals/` dir if empty after session

7. **Rollback**: walks directory tree for `_originals/` folders, moves every file back to parent directory, removes empty `_originals/`, removes `vcomp-log.json`. Same scan logic as `clean`.

## Risks / Trade-offs

- **[Data loss on incomplete move]** Pre-compression move means the original is in `_originals/` during compression. If the move itself fails (disk full, permissions), compression is aborted for that file.
  → Mitigation: wrap move in try/except, return error result.
- **[Disk space]** During compression, the original is in `_originals/` AND the compressed file is being written at the target path — both exist simultaneously.
  → Mitigation: same as current behavior; not new.
- **[Compression failure]**: Original is already in `_originals/` and safe — user can retry or rollback.

## Open Questions

None.
