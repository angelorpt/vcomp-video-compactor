import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class CompressionLogger:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._files: list[dict] = []
        self._session = "interrupted"

    def log_file(
        self,
        file_path: str,
        status: str,
        input_size: int = 0,
        output_size: int = 0,
        error: Optional[str] = None,
    ):
        entry = {
            "file": file_path,
            "status": status,
            "input_size": input_size,
            "output_size": output_size,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._files.append(entry)
        self._write()

    def finalize(self, session: str = "completed"):
        self._session = session
        self._write()

    def _write(self):
        data = {
            "session": self._session,
            "files": self._files,
        }
        fd, tmp_path = tempfile.mkstemp(
            dir=self.log_path.parent,
            prefix=f".{self.log_path.name}.tmp.",
        )
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, self.log_path)
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
