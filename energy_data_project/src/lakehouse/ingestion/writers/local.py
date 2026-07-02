from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path

from lakehouse.core.utils import ensure_directory


class LocalFileWriter:
    def write_bytes(self, content: bytes, path: Path) -> Path:
        """Salva bytes em disco. Se for ZIP, extrai o primeiro arquivo e retorna o path extraído."""
        ensure_directory(path.parent)

        if content[:2] == b"PK":
            with zipfile.ZipFile(BytesIO(content)) as zf:
                names = zf.namelist()
                inner_name = next((n for n in names if not n.endswith("/")), names[0])
                extracted_path = path.parent / inner_name
                zf.extract(inner_name, path.parent)
                return extracted_path

        path.write_bytes(content)
        return path
