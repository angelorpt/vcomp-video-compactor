import json
from pathlib import Path

from vcomp.logger import CompressionLogger


def test_log_format(tmp_path: Path):
    log_path = tmp_path / "vcomp-log.json"
    logger = CompressionLogger(log_path)

    logger.log_file(
        file_path="/path/to/video.mp4",
        status="completed",
        input_size=1000,
        output_size=300,
    )
    logger.finalize("completed")

    data = json.loads(log_path.read_text())
    assert data["session"] == "completed"
    assert len(data["files"]) == 1
    entry = data["files"][0]
    assert entry["file"] == "/path/to/video.mp4"
    assert entry["status"] == "completed"
    assert entry["input_size"] == 1000
    assert entry["output_size"] == 300
    assert entry["error"] is None
    assert "timestamp" in entry


def test_log_append(tmp_path: Path):
    log_path = tmp_path / "vcomp-log.json"
    logger = CompressionLogger(log_path)

    logger.log_file(
        file_path="a.mp4",
        status="completed",
        input_size=100,
        output_size=50,
    )
    logger.log_file(
        file_path="b.mp4",
        status="failed",
        error="something went wrong",
    )
    logger.finalize("completed")

    data = json.loads(log_path.read_text())
    assert len(data["files"]) == 2
    assert data["files"][0]["file"] == "a.mp4"
    assert data["files"][0]["status"] == "completed"
    assert data["files"][1]["file"] == "b.mp4"
    assert data["files"][1]["status"] == "failed"
    assert data["files"][1]["error"] == "something went wrong"
    assert data["session"] == "completed"


def test_log_interrupted_session(tmp_path: Path):
    log_path = tmp_path / "vcomp-log.json"
    logger = CompressionLogger(log_path)

    logger.log_file(
        file_path="a.mp4",
        status="completed",
        input_size=100,
        output_size=50,
    )

    data = json.loads(log_path.read_text())
    assert data["session"] == "interrupted"
    assert len(data["files"]) == 1


def test_log_atomic_write(tmp_path: Path):
    log_path = tmp_path / "vcomp-log.json"
    logger = CompressionLogger(log_path)
    logger.log_file(
        file_path="test.mp4",
        status="completed",
        input_size=100,
        output_size=50,
    )
    logger.finalize("completed")

    data = json.loads(log_path.read_text())
    assert data["session"] == "completed"
    assert log_path.suffix == ".json"
