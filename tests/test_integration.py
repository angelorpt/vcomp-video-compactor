import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from vcomp.cli import app

runner = CliRunner()


def test_run_command_basic(video_dir: Path, mock_ffmpeg_path: str):
    result = runner.invoke(app, ["run", str(video_dir), "--jobs", "1"])
    assert result.exit_code == 0
    assert "Scanning" in result.stdout
    out = video_dir / "video1.mp4"
    assert out.exists()
    originals = video_dir / "_originals"
    assert originals.is_dir()
    assert (originals / "video1.mp4").exists()


def test_run_command_dry_run(video_dir: Path):
    result = runner.invoke(app, ["run", str(video_dir), "--dry-run"])
    assert result.exit_code == 0
    assert "Dry Run" in result.stdout


def test_run_command_recursive(video_dir: Path, mock_ffmpeg_path: str):
    result = runner.invoke(app, ["run", str(video_dir), "--recursive", "--jobs", "1"])
    assert result.exit_code == 0
    out = video_dir / "video1.mp4"
    assert out.exists()
    originals = video_dir / "_originals"
    assert originals.is_dir()


def test_run_command_clone_mode(video_dir: Path, tmp_path: Path, mock_ffmpeg_path: str):
    out_dir = tmp_path / "output"
    result = runner.invoke(app, [
        "run", str(video_dir),
        "--mode", "clone",
        "--output-dir", str(out_dir),
        "--jobs", "1",
    ])
    assert result.exit_code == 0
    assert (out_dir / "video1.mp4").exists()
    assert not (video_dir / "_originals").exists()


def test_run_command_skip_existing(video_dir: Path, mock_ffmpeg_path: str):
    first = runner.invoke(app, ["run", str(video_dir), "--mode", "keep", "--jobs", "1"])
    assert first.exit_code == 0
    originals = video_dir / "_originals"
    assert originals.is_dir()
    assert (originals / "video1.mp4").exists()
    second = runner.invoke(app, ["run", str(video_dir), "--mode", "keep", "--jobs", "1"])
    assert second.exit_code == 0
    assert "Skipped" in second.stdout


def test_run_command_overwrite(video_dir: Path, mock_ffmpeg_path: str):
    first = runner.invoke(app, ["run", str(video_dir), "--jobs", "1"])
    assert first.exit_code == 0
    out = video_dir / "video1.mp4"
    old_content = out.read_text()
    result = runner.invoke(app, ["run", str(video_dir), "--overwrite", "--jobs", "1"])
    assert result.exit_code == 0
    assert out.read_text() == old_content


def test_run_no_files(tmp_path: Path):
    result = runner.invoke(app, ["run", str(tmp_path)])
    assert result.exit_code == 0
    assert "No video files found" in result.stdout


def test_clean_command_no_backups(video_dir: Path):
    result = runner.invoke(app, ["clean", str(video_dir)])
    assert result.exit_code == 0
    assert "No _originals directories found" in result.stdout


def test_clean_command_dry_run(video_dir: Path):
    backup = video_dir / "_originals"
    backup.mkdir()
    (backup / "backup.mp4").write_bytes(b"x")
    result = runner.invoke(app, ["clean", str(video_dir), "--dry-run"])
    assert result.exit_code == 0
    assert backup.exists()


def test_clean_command_with_backup(video_dir: Path, mock_ffmpeg_path: str):
    runner.invoke(app, ["run", str(video_dir), "--mode", "keep", "--jobs", "1"])
    originals_dir = video_dir / "_originals"
    assert originals_dir.exists()

    result = runner.invoke(app, ["clean", str(video_dir)], input="y\n")
    assert result.exit_code == 0
    assert not originals_dir.exists()


def test_clean_command_logs(video_dir: Path, mock_ffmpeg_path: str):
    runner.invoke(app, ["run", str(video_dir), "--mode", "keep", "--jobs", "1"])
    log_file = video_dir / "vcomp-log.json"
    assert log_file.exists()

    originals_dir = video_dir / "_originals"
    assert originals_dir.exists()

    result = runner.invoke(app, ["clean", str(video_dir), "--logs"], input="y\n")
    assert result.exit_code == 0
    assert not log_file.exists()
    assert originals_dir.exists()


def test_rollback_command(video_dir: Path, mock_ffmpeg_path: str):
    runner.invoke(app, ["run", str(video_dir), "--mode", "keep", "--jobs", "1"])
    originals_dir = video_dir / "_originals"
    assert originals_dir.exists()
    assert (originals_dir / "video1.mp4").exists()
    assert (video_dir / "video1.mp4").exists()

    result = runner.invoke(app, ["rollback", str(video_dir)], input="y\n")
    assert result.exit_code == 0
    assert not originals_dir.exists()
    assert (video_dir / "video1.mp4").exists()


def test_rollback_dry_run(video_dir: Path, mock_ffmpeg_path: str):
    runner.invoke(app, ["run", str(video_dir), "--mode", "keep", "--jobs", "1"])
    originals_dir = video_dir / "_originals"
    assert originals_dir.exists()

    result = runner.invoke(app, ["rollback", str(video_dir), "--dry-run"])
    assert result.exit_code == 0
    assert originals_dir.exists()
