import shutil
import subprocess
import sys
from pathlib import Path
from typing import Generator

import pytest

from vcomp.models import OutputMode, VideoFile


@pytest.fixture
def sample_video(tmp_path: Path) -> Path:
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"fake video content")
    return video


@pytest.fixture
def sample_video_file(sample_video: Path) -> VideoFile:
    return VideoFile(path=sample_video, size_bytes=sample_video.stat().st_size)


@pytest.fixture
def video_dir(tmp_path: Path) -> Generator[Path, None, None]:
    (tmp_path / "sub").mkdir()
    v1 = tmp_path / "video1.mp4"
    v2 = tmp_path / "video2.mov"
    v3 = tmp_path / "sub" / "video3.avi"
    v1.write_bytes(b"content1")
    v2.write_bytes(b"content2")
    v3.write_bytes(b"content3")
    yield tmp_path


@pytest.fixture
def mock_ffmpeg(tmp_path: Path) -> Path:
    script = tmp_path / "ffmpeg"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import sys, shutil\n"
        "if '--version' in sys.argv or '-version' in sys.argv:\n"
        "    print('ffmpeg version mock with libx265')\n"
        "    sys.exit(0)\n"
        "if '-i' in sys.argv:\n"
        "    i = sys.argv.index('-i')\n"
        "    src = sys.argv[i + 1]\n"
        "    dst = sys.argv[-1]\n"
        "    shutil.copy2(src, dst)\n"
    )
    script.chmod(0o755)
    return script


@pytest.fixture
def mock_ffmpeg_path(mock_ffmpeg: Path) -> Generator[str, None, None]:
    import os
    old = os.environ.get("PATH", "")
    os.environ["PATH"] = f"{mock_ffmpeg.parent}:{old}"
    yield os.environ["PATH"]
    os.environ["PATH"] = old


@pytest.fixture
def originals_dir(video_dir: Path) -> Generator[Path, None, None]:
    orig = video_dir / "_originals"
    orig.mkdir()
    (orig / "backup1.mp4").write_bytes(b"backup")
    yield orig
    if orig.exists():
        shutil.rmtree(orig)
