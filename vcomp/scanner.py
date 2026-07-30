import os
from pathlib import Path
from typing import List

from .models import VideoFile

DEFAULT_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}


def scan_directory(
    directory: Path,
    recursive: bool = False,
    extensions: set = DEFAULT_EXTENSIONS,
) -> List[VideoFile]:
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    files: List[VideoFile] = []
    walk_fn = os.walk if recursive else _walk_nonrecursive

    for dirpath, _dirnames, filenames in walk_fn(str(directory)):
        for name in sorted(filenames):
            ext = Path(name).suffix.lower()
            if ext in extensions:
                full_path = Path(dirpath) / name
                files.append(VideoFile(path=full_path, size_bytes=full_path.stat().st_size))

    return files


def _walk_nonrecursive(top: str):
    entries = list(os.scandir(top))
    yield top, [], [e.name for e in entries if e.is_file()]
