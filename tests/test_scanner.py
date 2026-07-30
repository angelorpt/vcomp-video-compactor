from pathlib import Path

import pytest

from vcomp.scanner import DEFAULT_EXTENSIONS, scan_directory


def test_scan_non_recursive(video_dir: Path):
    files = scan_directory(video_dir, recursive=False)
    paths = {f.path.name for f in files}
    assert paths == {"video1.mp4", "video2.mov"}
    assert all(f.size_bytes > 0 for f in files)


def test_scan_recursive(video_dir: Path):
    files = scan_directory(video_dir, recursive=True)
    paths = {f.path.name for f in files}
    assert paths == {"video1.mp4", "video2.mov", "video3.avi"}


def test_scan_empty_dir(tmp_path: Path):
    files = scan_directory(tmp_path, recursive=False)
    assert files == []


def test_scan_custom_extensions(video_dir: Path):
    files = scan_directory(video_dir, recursive=False, extensions={".mov"})
    assert len(files) == 1
    assert files[0].path.suffix == ".mov"


def test_scan_no_match(video_dir: Path):
    files = scan_directory(video_dir, recursive=False, extensions={".mkv"})
    assert files == []


def test_scan_not_a_directory(tmp_path: Path):
    f = tmp_path / "file.txt"
    f.write_text("x")
    with pytest.raises(NotADirectoryError):
        scan_directory(f)


def test_default_extensions():
    assert ".mp4" in DEFAULT_EXTENSIONS
    assert ".mov" in DEFAULT_EXTENSIONS
    assert ".avi" in DEFAULT_EXTENSIONS
