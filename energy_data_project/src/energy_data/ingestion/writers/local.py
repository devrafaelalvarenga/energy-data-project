from __future__ import annotations

from pathlib import Path


class LocalFileWriter:
    """Escreve arquivos binários em disco local."""

    def write_bytes(self, content: bytes, path: str | Path) -> None:
        """Escreve um arquivo binário criando diretórios quando necessário."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)