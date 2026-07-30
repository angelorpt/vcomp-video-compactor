from pathlib import Path
from typing import Optional

from .models import OutputMode, VideoFile


def build_output_path(video: VideoFile, input_dir: Path, output_dir: Optional[Path], mode: OutputMode) -> Path:
    if mode == OutputMode.SEPARATE:
        assert output_dir is not None, "--output-dir required for separate mode"
        rel = video.path.relative_to(input_dir.resolve())
        return (output_dir.resolve() / rel).with_suffix(video.path.suffix)

    parent = video.path.parent
    stem = video.path.stem
    ext = video.path.suffix
    return parent / f"{stem}_compactado{ext}"
