from __future__ import annotations

from pathlib import Path

import polars as pl


class ParquetWriter:
    """Escreve DataFrames Polars em formato Parquet."""

    def write(self, df: pl.DataFrame, path: str | Path) -> None:
        """Salva o DataFrame em formato Parquet."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        df.write_parquet(target)