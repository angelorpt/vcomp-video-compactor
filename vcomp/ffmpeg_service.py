import subprocess
import time
from pathlib import Path
from typing import List

from .models import CompressionResult, CompressionTask, OutputMode

FFMPEG_CMD = "ffmpeg"


def build_ffmpeg_cmd(task: CompressionTask) -> List[str]:
    return [
        FFMPEG_CMD, "-i", str(task.video.path),
        "-c:v", "libx265",
        "-crf", str(task.crf),
        "-preset", task.preset,
        "-c:a", "aac",
        "-b:a", task.audio_bitrate,
        "-y",
        str(task.output_path),
    ]


def execute_ffmpeg(task: CompressionTask) -> CompressionResult:
    start = time.time()
    result = CompressionResult(
        input_path=task.video.path,
        output_path=task.output_path,
        input_size=task.video.size_bytes,
    )
    try:
        task.output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = build_ffmpeg_cmd(task)
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=86400)
        result.output_size = task.output_path.stat().st_size
        result.success = True

        if task.mode == OutputMode.BACKUP:
            backup_dir = task.video.path.parent / ".originais"
            backup_dir.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.move(str(task.video.path), str(backup_dir / task.video.path.name))
        elif task.mode == OutputMode.DELETE:
            task.video.path.unlink()

    except subprocess.CalledProcessError as e:
        result.error = e.stderr.strip() or f"ffmpeg exited with code {e.returncode}"
        if task.output_path.exists():
            task.output_path.unlink()
    except Exception as e:
        result.error = str(e)
        if task.output_path.exists():
            task.output_path.unlink()

    result.elapsed_seconds = time.time() - start
    return result
