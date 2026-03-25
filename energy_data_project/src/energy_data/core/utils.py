from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_bytes(content: bytes) -> str:
    """Gera hash SHA-256 de um conteúdo binário."""
    return hashlib.sha256(content).hexdigest()


def ensure_directory(path: str | Path) -> Path:
    """Garante que o diretório exista."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory