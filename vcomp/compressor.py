import os
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, List, Optional

from .ffmpeg_service import execute_ffmpeg
from .logger import CompressionLogger
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


def _detect_resume(input_dir: Path) -> Optional[List[VideoFile]]:
    originals_dir = input_dir / "_originals"
    if not originals_dir.is_dir():
        return None
    files = []
    for f in sorted(originals_dir.iterdir()):
        if f.is_file():
            files.append(VideoFile(path=f, size_bytes=f.stat().st_size))
    return files if files else None


def compress_videos(
    videos: List[VideoFile],
    crf: int = 28,
    preset: str = "medium",
    audio_bitrate: str = "128k",
    mode: OutputMode = OutputMode.KEEP,
    input_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    jobs: int = os.cpu_count() or 2,
    overwrite: bool = False,
    progress_callback: Optional[Callable] = None,
    log_path: Optional[Path] = None,
) -> List[CompressionResult]:
    results: List[CompressionResult] = []
    tasks: List[CompressionTask] = []

    base_dir = input_dir or videos[0].path.parent if videos else Path()

    resume_files = _detect_resume(base_dir)
    if resume_files is not None:
        videos = resume_files

    logger = CompressionLogger(log_path) if log_path else None

    for video in videos:
        if video.path.parent.name == "_originals":
            out = video.path.parent.parent / video.path.name
        else:
            out = build_output_path(video, base_dir, output_dir, mode)

        if out.exists() and out != video.path and not overwrite:
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
            if logger:
                logger.log_file(str(video.path), "skipped", input_size=video.size_bytes)
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
            if logger:
                logger.log_file(
                    str(res.input_path),
                    "completed" if res.success else "failed",
                    input_size=res.input_size,
                    output_size=res.output_size,
                    error=res.error,
                )

    if logger:
        logger.finalize("completed")

    return results
