from pathlib import Path
from typing import List, Optional, Protocol

from .models import CompressionResult, CompressionTask, OutputMode, VideoFile


class FFmpegExecutor(Protocol):
    def execute(self, task: CompressionTask) -> CompressionResult: ...


class PathResolver(Protocol):
    def resolve(self, video: VideoFile, input_dir: Path, output_dir: Optional[Path], mode: OutputMode) -> Path: ...


class PrerequisiteChecker(Protocol):
    def check(self) -> None: ...
