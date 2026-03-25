from __future__ import annotations

from pathlib import Path

import polars as pl


class SilverWriter:
    """Responsável por persistir a camada Silver."""

    def write(self, df: pl.DataFrame, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        df.write_parquet(target)