import os
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, List, Optional

from .ffmpeg_service import execute_ffmpeg
from .models import CompressionResult, CompressionTask, OutputMode, VideoFile
from .path_resolver import build_output_path

FFMPEG_CMD = "ffmpeg"


def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(
            [FFMPEG_CMD, "-version"], capture_output=True, text=True, timeout=5
        )
        return "libx265" in result.stdout or "libx265" in result.stderr
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _compress_single(task: CompressionTask) -> CompressionResult:
    return execute_ffmpeg(task)


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
    tasks: List[CompressionTask] = []

    base_dir = input_dir or videos[0].path.parent if videos else Path()

    for video in videos:
        out = build_output_path(video, base_dir, output_dir, mode)
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
        tasks.append(CompressionTask(
            video=video,
            output_path=out,
            crf=crf,
            preset=preset,
            audio_bitrate=audio_bitrate,
            mode=mode,
        ))

    with ProcessPoolExecutor(max_workers=jobs) as executor:
        futures = {executor.submit(_compress_single, t): t.video for t in tasks}
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            if progress_callback:
                progress_callback(res)

    return results
