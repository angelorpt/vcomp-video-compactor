from pathlib import Path

import pytest

from vcomp.ffmpeg_service import build_ffmpeg_cmd, execute_ffmpeg, _originals_path
from vcomp.models import CompressionTask, OutputMode, VideoFile


def test_build_ffmpeg_cmd_defaults(sample_video: Path, tmp_path: Path):
    task = CompressionTask(
        video=VideoFile(path=sample_video, size_bytes=10),
        output_path=tmp_path / "out.mp4",
        crf=28,
        preset="medium",
        audio_bitrate="128k",
        mode=OutputMode.KEEP,
    )
    cmd = build_ffmpeg_cmd(task)
    assert cmd[0] == "ffmpeg"
    assert "-i" in cmd
    assert str(sample_video) in cmd
    assert "-c:v" in cmd
    assert "libx265" in cmd
    assert "-crf" in cmd
    assert "28" in cmd
    assert "-preset" in cmd
    assert "medium" in cmd
    assert "-c:a" in cmd
    assert "aac" in cmd
    assert "-b:a" in cmd
    assert "128k" in cmd
    assert "-y" in cmd
    assert str(task.output_path) in cmd


def test_build_ffmpeg_cmd_custom(sample_video: Path, tmp_path: Path):
    task = CompressionTask(
        video=VideoFile(path=sample_video, size_bytes=10),
        output_path=tmp_path / "out.mkv",
        crf=24,
        preset="slow",
        audio_bitrate="192k",
        mode=OutputMode.REPLACE,
    )
    cmd = build_ffmpeg_cmd(task)
    assert "24" in cmd
    assert "slow" in cmd
    assert "192k" in cmd
    assert str(task.output_path) in cmd


def test_execute_ffmpeg_keep_moves_to_originals(sample_video: Path, tmp_path: Path, mock_ffmpeg_path: str):
    out = tmp_path / "out.mp4"
    task = CompressionTask(
        video=VideoFile(path=sample_video, size_bytes=sample_video.stat().st_size),
        output_path=out,
        crf=28,
        preset="medium",
        audio_bitrate="128k",
        mode=OutputMode.KEEP,
    )
    result = execute_ffmpeg(task)
    assert result.success is True
    assert not sample_video.exists()
    orig = _originals_path(task)
    assert orig.exists()
    assert out.exists()


def test_execute_ffmpeg_replace_cleans_originals(sample_video: Path, tmp_path: Path, mock_ffmpeg_path: str):
    out = tmp_path / "out.mp4"
    task = CompressionTask(
        video=VideoFile(path=sample_video, size_bytes=sample_video.stat().st_size),
        output_path=out,
        crf=28,
        preset="medium",
        audio_bitrate="128k",
        mode=OutputMode.REPLACE,
    )
    result = execute_ffmpeg(task)
    assert result.success is True
    assert not (task.video.path.parent / "_originals").exists()
    assert out.exists()


def test_execute_ffmpeg_clone_does_not_move(sample_video: Path, tmp_path: Path, mock_ffmpeg_path: str):
    out = tmp_path / "out.mp4"
    task = CompressionTask(
        video=VideoFile(path=sample_video, size_bytes=sample_video.stat().st_size),
        output_path=out,
        crf=28,
        preset="medium",
        audio_bitrate="128k",
        mode=OutputMode.CLONE,
    )
    result = execute_ffmpeg(task)
    assert result.success is True
    assert sample_video.exists()
    assert not (task.video.path.parent / "_originals").exists()
