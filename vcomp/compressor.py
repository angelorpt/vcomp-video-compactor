import os
import shutil
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, List, Optional

from .models import CompressionResult, OutputMode, VideoFile

FFMPEG_CMD = "ffmpeg"


def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(
            [FFMPEG_CMD, "-version"], capture_output=True, text=True, timeout=5
        )
        return "libx265" in result.stdout or "libx265" in result.stderr
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _build_output_path(video: VideoFile, input_dir: Path, output_dir: Optional[Path], mode: OutputMode) -> Path:
    if mode == OutputMode.SEPARATE:
        assert output_dir is not None, "--output-dir required for separate mode"
        rel = video.path.relative_to(input_dir.resolve())
        return (output_dir.resolve() / rel).with_suffix(video.path.suffix)
    parent = video.path.parent
    stem = video.path.stem
    ext = video.path.suffix
    return parent / f"{stem}_compactado{ext}"


def _compress_single(args: tuple) -> CompressionResult:
    video, output_path, crf, preset, audio_bitrate, mode = args
    start = time.time()
    result = CompressionResult(
        input_path=video.path, output_path=output_path, input_size=video.size_bytes
    )
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            FFMPEG_CMD, "-i", str(video.path),
            "-c:v", "libx265",
            "-crf", str(crf),
            "-preset", preset,
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-y",
            str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=86400)
        result.output_size = output_path.stat().st_size
        result.success = True

        if mode == OutputMode.BACKUP:
            backup_dir = video.path.parent / ".originais"
            backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(video.path), str(backup_dir / video.path.name))
        elif mode == OutputMode.DELETE:
            video.path.unlink()

    except subprocess.CalledProcessError as e:
        result.error = e.stderr.strip() or f"ffmpeg exited with code {e.returncode}"
        if output_path.exists():
            output_path.unlink()
    except Exception as e:
        result.error = str(e)
        if output_path.exists():
            output_path.unlink()

    result.elapsed_seconds = time.time() - start
    return result


def compress_videos(
    videos: List[VideoFile],
    crf: int = 28,
    preset: str = "medium",
    audio_bitrate: str = "128k",
    mode: OutputMode = OutputMode.SAME,
    input_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    jobs: int = os.cpu_count() or 2,
    overwrite: bool = False,
    progress_callback: Optional[Callable] = None,
) -> List[CompressionResult]:
    results: List[CompressionResult] = []
    tasks = []

    base_dir = input_dir or videos[0].path.parent if videos else Path()

    for video in videos:
        out = _build_output_path(video, base_dir, output_dir, mode)
        if out.exists() and not overwrite:
            result = CompressionResult(
                input_path=video.path,
                output_path=out,
                success=False,
                input_size=video.size_bytes,
                error="Skipped (already exists)",
            )
            results.append(result)
            if progress_callback:
                progress_callback(result)
            continue
        tasks.append((video, out, crf, preset, audio_bitrate, mode))

    with ProcessPoolExecutor(max_workers=jobs) as executor:
        futures = {executor.submit(_compress_single, t): t[0] for t in tasks}
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            if progress_callback:
                progress_callback(res)

    return results
