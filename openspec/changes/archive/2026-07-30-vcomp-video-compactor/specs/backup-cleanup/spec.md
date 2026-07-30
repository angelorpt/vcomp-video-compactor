# Backup Cleanup

## Capability

Subcommand to find and remove `.originais/` backup directories.

## Requirements

### REQ-BC-01: Scan for backups
- `vcomp clean [directory]` MUST scan the given directory (or current dir if omitted) for `.originais/` folders
- With `--recursive` / `-r`, MUST find `.originais/` in all subdirectories
- Without recursion, only checks the immediate directory

### REQ-BC-02: Dry-run mode
- `--dry-run` MUST list all `.originais/` directories and their total size without deleting

### REQ-BC-03: Deletion
- Before deleting, MUST show a summary of what will be removed and ask for confirmation
- After confirmation, delete all identified `.originais/` directories

### REQ-BC-04: Output
- MUST show a summary: directories found, total size, directories deleted, errors
