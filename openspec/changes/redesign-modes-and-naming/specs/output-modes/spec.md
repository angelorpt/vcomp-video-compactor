## RENAMED Requirements

### Requirement: Same-directory mode (`--mode same`)
- FROM: `same`
- TO: `keep`

### Requirement: Backup mode (`--mode backup`)
**Reason**: Removed. The standard flow now always moves originals to `_originals/`. `keep` mode preserves `_originals/`; `replace` mode auto-deletes on success.
**Migration**: Use `--mode keep` and run `vcomp clean` manually to purge `_originals/`.

### Requirement: Delete mode (`--mode delete`)
- FROM: `delete`
- TO: `replace`

### Requirement: Separate directory mode (`--mode separate`)
- FROM: `separate`
- TO: `clone`

## MODIFIED Requirements

### Requirement: Keep mode (`--mode keep`)
The system MUST move the original file to `_originals/` directory before compression. The compressed output MUST replace the original at its original path with the **same filename** (no `_compactado` suffix). The `_originals/` directory MUST NOT be deleted automatically — user runs `vcomp clean` to remove it.

#### Scenario: Basic keep compression
- **WHEN** user runs `vcomp run --mode keep <dir>` on `video.mp4`
- **THEN** the original is moved to `<dir>/_originals/video.mp4`
- **AND** compressed output is written to `<dir>/video.mp4`
- **AND** `_originals/` persists after the session

### Requirement: Replace mode (`--mode replace`)
The system MUST move the original to `_originals/` before compression, same as `keep`. After **each** file compresses successfully, the system MUST delete that file from `_originals/` immediately. If all files in a session succeed, `_originals/` MUST be removed if empty.

#### Scenario: Successful replace session
- **WHEN** user runs `vcomp run --mode replace <dir>` on 3 files
- **AND** all 3 compress successfully
- **THEN** each original is deleted from `_originals/` per-file as it completes
- **AND** `_originals/` is removed when the last file is done

#### Scenario: Replace with failures
- **WHEN** one file fails compression
- **THEN** that file's original remains in `_originals/`
- **AND** the user is notified about the failure in the session summary

### Requirement: Clone mode (`--mode clone`)
Same as previous `separate` — requires `--output-dir` / `-o`. Output directory mirrors input directory structure. Original filename is preserved. Original file is **not** moved to `_originals/`.

#### Scenario: Clone compression
- **WHEN** user runs `vcomp run --mode clone --output-dir /output <input>`
- **AND** input contains `input/course/video.mp4`
- **THEN** output is written to `/output/course/video.mp4`
- **AND** original at `input/course/video.mp4` is untouched

### Requirement: Overwrite protection
If a compressed output file already exists at the target path, the system MUST skip compression for that file. The `--overwrite` flag forces re-compression even if output exists.

#### Scenario: Skip existing output
- **WHEN** `video.mp4` already exists at the target path
- **THEN** compression is skipped
- **AND** the skip is reported in the session summary

#### Scenario: Force re-compression
- **WHEN** `--overwrite` is set
- **AND** `video.mp4` exists at the target path
- **THEN** compression proceeds and overwrites the file

### Requirement: Original handling
Before compression starts, the system MUST move the original file to `<parent>/_originals/<filename>` for `keep` and `replace` modes. If a previous run left files in `_originals/` (interrupted session), those files MUST be used as the source for compression on resume.

#### Scenario: Fresh run
- **WHEN** no `_originals/` exists
- **THEN** originals are moved to `_originals/` and compressed from there

#### Scenario: Resume interrupted run
- **WHEN** `_originals/` exists with files from a previous interrupted run
- **THEN** only files in `_originals/` are processed
- **AND** files already compressed (present at target path) are skipped

## ADDED Requirements

### Requirement: Session logging
The system MUST write a JSON log file at `<processed-dir>/vcomp-log.json` after each session. The log MUST contain an array of per-file entries plus a session status field.

#### Scenario: Log on successful session
- **WHEN** a compression session completes
- **THEN** a `vcomp-log.json` file exists at the processed root directory
- **AND** contains entries for each file with `status: "completed"`, original and compressed sizes
- **AND** contains `session: "completed"`

#### Scenario: Log on interrupted session
- **WHEN** a session is interrupted (Ctrl+C)
- **THEN** the log records all files completed so far
- **AND** `session` is absent or set to `"interrupted"`

#### Scenario: Log on failed file
- **WHEN** a file fails compression
- **THEN** the log records `status: "failed"` with the error message
- **AND** `session` is `"completed"` only if all files finished (success or failure)

### Requirement: Resume on re-run
When `vcomp run` is invoked on a directory that already has a `_originals/` directory with content, the system MUST process only the files present in `_originals/` and skip files that already have a compressed output at the target path. Files that failed previously are retried.

#### Scenario: Resume after partial run
- **WHEN** previous run was interrupted after 2 of 5 files completed
- **AND** user runs `vcomp run <dir>` again
- **THEN** the 2 completed files are skipped
- **AND** the remaining 3 files are processed

### Requirement: Clean logs flag
`vcomp clean --logs` / `-l` MUST scan for and delete `vcomp-log.json` files in the target directories, without touching `_originals/` folders.

#### Scenario: Clean logs only
- **WHEN** user runs `vcomp clean --logs <dir>`
- **THEN** all `vcomp-log.json` files under `<dir>` are deleted
- **AND** `_originals/` directories are preserved

### Requirement: Rollback command
`vcomp rollback [directory]` MUST restore originals from `_originals/` back to their original locations, overwriting any compressed files. After restoration, it MUST delete the `_originals/` directories and all `vcomp-log.json` files.

#### Scenario: Full rollback
- **WHEN** user runs `vcomp rollback <dir>`
- **THEN** originals in `<dir>/**/_originals/` are moved back to their parent directories
- **AND** compressed files at the target paths are overwritten
- **AND** all `<dir>/**/_originals/` directories are removed
- **AND** all `<dir>/**/vcomp-log.json` files are removed
