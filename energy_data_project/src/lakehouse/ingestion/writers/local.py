from __future__ import annotations

from pathlib import Path

from lakehouse.core.utils import ensure_directory


class LocalFileWriter:
    def write_bytes(self, content: bytes, path: Path) -> None:
        ensure_directory(path.parent)
        path.write_bytes(content)
