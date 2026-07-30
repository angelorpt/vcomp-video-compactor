from pathlib import Path

import pytest

from vcomp.models import OutputMode, VideoFile
from vcomp.path_resolver import build_output_path


def test_keep_mode(sample_video_file: VideoFile):
    result = build_output_path(sample_video_file, sample_video_file.path.parent, None, OutputMode.KEEP)
    assert result == sample_video_file.path


def test_replace_mode(sample_video_file: VideoFile):
    result = build_output_path(sample_video_file, sample_video_file.path.parent, None, OutputMode.REPLACE)
    assert result == sample_video_file.path


def test_clone_mode(sample_video_file: VideoFile, tmp_path: Path):
    output_dir = tmp_path / "output"
    result = build_output_path(sample_video_file, sample_video_file.path.parent, output_dir, OutputMode.CLONE)
    assert output_dir.resolve() in result.parents
    assert result.suffix == sample_video_file.path.suffix


def test_clone_mode_nested(video_dir: Path):
    sub_video = video_dir / "sub" / "video3.avi"
    vf = VideoFile(path=sub_video, size_bytes=sub_video.stat().st_size)
    output_dir = video_dir / "out"
    result = build_output_path(vf, video_dir, output_dir, OutputMode.CLONE)
    assert result == (output_dir.resolve() / "sub" / "video3.avi")


def test_clone_mode_no_output_dir(sample_video_file: VideoFile):
    with pytest.raises(AssertionError):
        build_output_path(sample_video_file, sample_video_file.path.parent, None, OutputMode.CLONE)


def test_with_relative_input_dir(sample_video_file: VideoFile, tmp_path: Path):
    output_dir = tmp_path / "out"
    result = build_output_path(sample_video_file, sample_video_file.path.parent, output_dir, OutputMode.CLONE)
    assert result.suffix == sample_video_file.path.suffix
