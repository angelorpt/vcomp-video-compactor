from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class OutputMode(str, Enum):
    SAME = "same"
    BACKUP = "backup"
    DELETE = "delete"
    SEPARATE = "separate"


@dataclass
class VideoFile:
    path: Path
    size_bytes: int = 0

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()

    @property
    def stem(self) -> str:
        return self.path.stem


@dataclass
class CompressionResult:
    input_path: Path
    output_path: Path
    success: bool = False
    input_size: int = 0
    output_size: int = 0
    error: Optional[str] = None
    elapsed_seconds: float = 0.0

    @property
    def saved_bytes(self) -> int:
        return self.input_size - self.output_size

    @property
    def ratio(self) -> float:
        if self.input_size == 0:
            return 0.0
        return (self.output_size / self.input_size) * 100


@dataclass
class CompressionReport:
    results: list = field(default_factory=list)
    total_errors: int = 0
    total_skipped: int = 0

    @property
    def total_input_size(self) -> int:
        return sum(r.input_size for r in self.results if r.success)

    @property
    def total_output_size(self) -> int:
        return sum(r.output_size for r in self.results if r.success)

    @property
    def total_saved(self) -> int:
        return self.total_input_size - self.total_output_size

    @property
    def successful(self) -> list:
        return [r for r in self.results if r.success]
