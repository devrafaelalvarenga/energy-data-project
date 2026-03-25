from __future__ import annotations

import polars as pl

from energy_data.core.logging import get_logger
from energy_data.silver.transformations import (
    cast_types,
    clean_strings,
    drop_invalid_rows,
    enrich,
    normalize_columns,
)
from energy_data.silver.validators import validate_silver
from energy_data.silver.writer import SilverWriter


logger = get_logger(__name__)


class SilverProcessor:
    """Processa dados da Bronze e gera a camada Silver."""

    def __init__(self, writer: SilverWriter) -> None:
        self.writer = writer

    def run(self, bronze_path: str, silver_path: str) -> None:
        logger.info("silver.started", bronze_path=bronze_path)

        df = pl.read_parquet(bronze_path)
        df = normalize_columns(df)
        df = clean_strings(df)
        df = cast_types(df)
        df = enrich(df)

        logger.info("silver.columns", columns=df.columns)

        if "sigla_indicador" in df.columns:
            logger.info(
                "silver.invalid_sigla_indicador_before_drop",
                count=df.filter(
                    pl.col("sigla_indicador").is_null()
                ).height,
            )

        df = drop_invalid_rows(df)
        validate_silver(df)

        self.writer.write(df, silver_path)

        logger.info(
            "silver.completed",
            rows=df.height,
            columns=df.width,
            silver_path=silver_path,
        )