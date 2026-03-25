from __future__ import annotations

from io import BytesIO

import polars as pl

from energy_data.core.exceptions import IngestionError


class CsvReader:
    """Lê conteúdo CSV em memória e retorna DataFrame Polars."""

    def read(
        self,
        content: bytes,
        separator: str = ";",
        encoding: str = "latin-1",
        infer_schema_length: int = 1000,
    ) -> pl.DataFrame:
        """
        Converte bytes CSV em DataFrame Polars.

        Raises:
            IngestionError: quando o parsing falha.
        """
        try:
            return pl.read_csv(
                BytesIO(content),
                separator=separator,
                encoding=encoding,
                infer_schema_length=infer_schema_length,
                ignore_errors=False,
                truncate_ragged_lines=False,
            )
        except Exception as exc:
            raise IngestionError("Falha ao ler o CSV com Polars.") from exc