# Output Modes

## Capability

Handle different strategies for placing compressed files and managing originals.

## Requirements

### REQ-OM-01: Same-directory mode (`--mode same`)
- Compressed file MUST be placed next to the original
- Naming convention: `<original_name>_compactado.<ext>`
- Example: `video.mp4` → `video_compactado.mp4`

### REQ-OM-02: Backup mode (`--mode backup`)
- Compressed file placed next to the original (same naming as `same`)
- Original file MUST be moved to a `.originais/` subdirectory
- The `.originais/` directory MUST mirror the original directory structure

### REQ-OM-03: Delete mode (`--mode delete`)
- Compressed file placed next to the original
- Original file MUST be deleted after successful compression

### REQ-OM-04: Separate directory mode (`--mode separate`)
- Requires `--output-dir` / `-o` flag
- Output directory structure MUST mirror the input directory structure
- Naming: original filename preserved (no `_compactado` suffix)
- Example: `input/course/video.mp4` → `output/course/video.mp4`

### REQ-OM-05: Overwrite protection
- If the output file already exists, the tool MUST skip compression for that file
- `--overwrite` flag forces re-compression even if output exists

### REQ-OM-06: Rollback safety
- In `backup` mode, if compression fails for a file, the original MUST NOT be moved to `.originais/`
- In `delete` mode, if compression fails, the original MUST be preserved
