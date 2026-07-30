## MODIFIED Requirements

### Requirement: Scan for originals backups
`vcomp clean [directory]` MUST scan the given directory (or current dir if omitted) for `_originals/` folders. With `--recursive` / `-r`, MUST find `_originals/` in all subdirectories. Without recursion, only checks the immediate directory.

#### Scenario: Scan recursive
- **WHEN** user runs `vcomp clean --recursive <dir>`
- **THEN** all `_originals/` directories under `<dir>` are listed

#### Scenario: Scan non-recursive
- **WHEN** user runs `vcomp clean <dir>`
- **THEN** only `<dir>/_originals/` is checked

### Requirement: Deletion summary and confirmation
Before deleting, MUST show a summary of what will be removed and total size, then ask for confirmation.

#### Scenario: Confirm deletion
- **WHEN** `_originals/` directories are found
- **THEN** a table with paths and sizes is displayed
- **AND** user is prompted to confirm before deletion

### Requirement: Output summary
MUST show a summary: directories found, total size, directories deleted, errors.

#### Scenario: Deletion result
- **WHEN** deletion completes
- **THEN** summary shows count of deleted directories and any errors

## ADDED Requirements

### Requirement: Clean logs flag
`vcomp clean --logs` / `-l` MUST scan for and remove `vcomp-log.json` files only, without affecting `_originals/` directories.

#### Scenario: Remove only logs
- **WHEN** user runs `vcomp clean --logs <dir>`
- **THEN** all `vcomp-log.json` files under `<dir>` are deleted
- **AND** `_originals/` directories are preserved
- **AND** a summary is displayed with number of log files removed

### Requirement: Rollback command
`vcomp rollback [directory]` MUST restore originals from `_originals/` back to their original parent locations, overwriting any compressed files present. After restoration it MUST delete all `_originals/` directories and `vcomp-log.json` files.

#### Scenario: Rollback restores originals
- **WHEN** user runs `vcomp rollback <dir>`
- **THEN** each file in `<dir>/**/_originals/` is moved back to its parent directory
- **AND** compressed files at target paths are overwritten
- **AND** all `_originals/` directories under `<dir>` are removed
- **AND** all `vcomp-log.json` files under `<dir>` are removed
- **AND** summary shows number of restored and deleted items

#### Scenario: Rollback with confirmation
- **WHEN** `_originals/` directories are found
- **THEN** a summary of what will be restored and deleted is shown
- **AND** user is prompted to confirm before proceeding

#### Scenario: Rollback dry-run
- **WHEN** user runs `vcomp rollback --dry-run <dir>`
- **THEN** lists what would be restored and deleted without executing
