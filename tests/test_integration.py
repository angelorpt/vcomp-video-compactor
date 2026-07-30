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
    compactado = video_dir / "video1_compactado.mp4"
    assert compactado.exists()


def test_run_command_dry_run(video_dir: Path):
    result = runner.invoke(app, ["run", str(video_dir), "--dry-run"])
    assert result.exit_code == 0
    assert "Dry Run" in result.stdout


def test_run_command_recursive(video_dir: Path, mock_ffmpeg_path: str):
    result = runner.invoke(app, ["run", str(video_dir), "--recursive", "--jobs", "1"])
    assert result.exit_code == 0
    compactado = video_dir / "video1_compactado.mp4"
    assert compactado.exists()


def test_run_command_separate_mode(video_dir: Path, tmp_path: Path, mock_ffmpeg_path: str):
    out_dir = tmp_path / "output"
    result = runner.invoke(app, [
        "run", str(video_dir),
        "--mode", "separate",
        "--output-dir", str(out_dir),
        "--jobs", "1",
    ])
    assert result.exit_code == 0
    assert (out_dir / "video1.mp4").exists()


def test_run_command_skip_existing(video_dir: Path, mock_ffmpeg_path: str):
    compactado = video_dir / "video1_compactado.mp4"
    compactado.write_text("existing")
    result = runner.invoke(app, ["run", str(video_dir), "--jobs", "1"])
    assert result.exit_code == 0
    assert "Skipped" in result.stdout


def test_run_command_overwrite(video_dir: Path, mock_ffmpeg_path: str):
    compactado = video_dir / "video1_compactado.mp4"
    compactado.write_text("old")
    result = runner.invoke(app, ["run", str(video_dir), "--overwrite", "--jobs", "1"])
    assert result.exit_code == 0
    assert compactado.read_text() != "old"


def test_run_no_files(tmp_path: Path):
    result = runner.invoke(app, ["run", str(tmp_path)])
    assert result.exit_code == 0
    assert "No video files found" in result.stdout


def test_clean_command_no_backups(video_dir: Path):
    result = runner.invoke(app, ["clean", str(video_dir)])
    assert result.exit_code == 0
    assert "No .originais/ directories found" in result.stdout


def test_clean_command_dry_run(video_dir: Path):
    backup = video_dir / ".originais"
    backup.mkdir()
    (backup / "backup.mp4").write_bytes(b"x")
    result = runner.invoke(app, ["clean", str(video_dir), "--dry-run"])
    assert result.exit_code == 0
    assert backup.exists()


def test_clean_command_with_backup(video_dir: Path, mock_ffmpeg_path: str):
    runner.invoke(app, ["run", str(video_dir), "--mode", "backup", "--jobs", "1"])
    backup_dir = video_dir / ".originais"
    assert backup_dir.exists()

    result = runner.invoke(app, ["clean", str(video_dir)], input="y\n")
    assert result.exit_code == 0
    assert not backup_dir.exists()
