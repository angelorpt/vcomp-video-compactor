# Compress Videos

## Capability

Scan a directory for video files and compress them using ffmpeg with libx265.

## Requirements

### REQ-CV-01: Directory scanning
- The tool MUST scan a user-provided directory path for video files
- When `--recursive` / `-r` is set, the scan MUST descend into subdirectories
- Without `--recursive`, only files in the immediate directory are collected

### REQ-CV-02: File filtering
- Default extensions: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.m4v`
- The user MUST be able to override extensions via `--extensions`

### REQ-CV-03: ffmpeg execution
- Each video MUST be compressed with: `ffmpeg -i <input> -c:v libx265 -crf <N> -c:a aac -b:a <rate> <output>`
- CRF defaults to 28, configurable via `--crf`
- Audio bitrate defaults to `128k`, configurable via `--audio-bitrate`
- x265 preset defaults to `medium`, configurable via `--preset`

### REQ-CV-04: Parallelism
- Multiple videos MUST be compressed concurrently using a process pool
- Number of parallel jobs defaults to the number of available CPU cores
- Configurable via `--jobs` / `-j`

### REQ-CV-05: Preview / dry-run
- With `--dry-run`, the tool MUST list all videos that would be compressed without executing ffmpeg
- Must show estimated output paths and sizes if available

### REQ-CV-06: Progress reporting
- A live progress bar MUST show: current file, overall progress, ETA, elapsed time
- On completion, a summary table MUST display: total files, compressed, skipped, errors, space saved
