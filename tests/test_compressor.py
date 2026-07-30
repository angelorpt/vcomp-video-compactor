import os
from pathlib import Path

from vcomp.compressor import _compress_single, check_ffmpeg, compress_videos
from vcomp.models import CompressionTask, OutputMode, VideoFile


def test_check_ffmpeg():
    assert check_ffmpeg() is True


def test_compress_single_success(sample_video: Path, tmp_path: Path, mock_ffmpeg_path: str):
    out = tmp_path / "out.mp4"
    task = CompressionTask(
        video=VideoFile(path=sample_video, size_bytes=sample_video.stat().st_size),
        output_path=out,
        crf=28,
        preset="medium",
        audio_bitrate="128k",
        mode=OutputMode.KEEP,
    )
    result = _compress_single(task)
    assert result.success is True
    assert result.input_path == sample_video
    assert result.output_path == out
    assert result.output_size > 0


def test_compress_single_keep_mode(sample_video: Path, tmp_path: Path, mock_ffmpeg_path: str):
    out = tmp_path / "out.mp4"
    task = CompressionTask(
        video=VideoFile(path=sample_video, size_bytes=sample_video.stat().st_size),
        output_path=out,
        crf=28,
        preset="medium",
        audio_bitrate="128k",
        mode=OutputMode.KEEP,
    )
    result = _compress_single(task)
    assert result.success is True
    originals_dir = sample_video.parent / "_originals"
    assert (originals_dir / sample_video.name).exists()


def test_compress_single_replace_mode(sample_video: Path, tmp_path: Path, mock_ffmpeg_path: str):
    out = tmp_path / "out.mp4"
    video_copy = tmp_path / "toreplace.mp4"
    video_copy.write_bytes(sample_video.read_bytes())
    task = CompressionTask(
        video=VideoFile(path=video_copy, size_bytes=video_copy.stat().st_size),
        output_path=out,
        crf=28,
        preset="medium",
        audio_bitrate="128k",
        mode=OutputMode.REPLACE,
    )
    result = _compress_single(task)
    assert result.success is True
    assert not video_copy.exists()
    assert not (tmp_path / "_originals").exists()


def test_compress_single_error_creates_output_dir(sample_video: Path, tmp_path: Path, mock_ffmpeg_path: str):
    nested_out = tmp_path / "nested" / "sub" / "out.mp4"
    task = CompressionTask(
        video=VideoFile(path=sample_video, size_bytes=sample_video.stat().st_size),
        output_path=nested_out,
        crf=28,
        preset="medium",
        audio_bitrate="128k",
        mode=OutputMode.KEEP,
    )
    result = _compress_single(task)
    assert result.success is True
    assert nested_out.exists()


def test_compress_videos_skip_existing(sample_video: Path, tmp_path: Path, mock_ffmpeg_path: str):
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    out = out_dir / sample_video.name
    out.write_text("existing")
    vf = VideoFile(path=sample_video, size_bytes=sample_video.stat().st_size)
    results = compress_videos(
        videos=[vf],
        input_dir=tmp_path,
        output_dir=out_dir,
        mode=OutputMode.CLONE,
        jobs=1,
    )
    assert len(results) == 1
    assert results[0].success is False
    assert results[0].error == "Skipped (already exists)"


def test_compress_videos_overwrite(tmp_path: Path, mock_ffmpeg_path: str):
    src = tmp_path / "video.mp4"
    src.write_bytes(b"content")
    out = tmp_path / "video.mp4"
    out.write_text("old")
    vf = VideoFile(path=src, size_bytes=src.stat().st_size)
    results = compress_videos(
        videos=[vf],
        input_dir=tmp_path,
        overwrite=True,
        jobs=1,
    )
    assert len(results) == 1
    assert results[0].success is True


def test_compress_videos_multiple(video_dir: Path, mock_ffmpeg_path: str):
    files = []
    for f in video_dir.iterdir():
        if f.is_file() and f.suffix in (".mp4", ".mov", ".avi"):
            files.append(VideoFile(path=f, size_bytes=f.stat().st_size))
    results = compress_videos(
        videos=files,
        input_dir=video_dir,
        jobs=2,
    )
    assert len(results) > 0
    successful = [r for r in results if r.success]
    assert len(successful) > 0


def test_compress_videos_keep_mode_originals_in_dir(video_dir: Path, mock_ffmpeg_path: str):
    files = [VideoFile(path=f, size_bytes=f.stat().st_size) for f in video_dir.iterdir() if f.suffix == ".mp4"]
    paths_before = {f.path for f in files}
    compress_videos(videos=files, input_dir=video_dir, mode=OutputMode.KEEP, jobs=1)
    originals_dir = video_dir / "_originals"
    assert originals_dir.is_dir()
    for p in paths_before:
        assert (originals_dir / p.name).exists(), f"{p.name} should be in _originals/"
        assert p.exists(), f"{p.name} should exist (compressed output)"


def test_detect_resume(video_dir: Path):
    from vcomp.compressor import _detect_resume
    assert _detect_resume(video_dir) is None
    originals_dir = video_dir / "_originals"
    originals_dir.mkdir()
    (originals_dir / "video1.mp4").write_bytes(b"backup")
    files = _detect_resume(video_dir)
    assert files is not None
    assert len(files) == 1
    assert files[0].path.name == "video1.mp4"
