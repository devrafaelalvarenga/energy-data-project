from __future__ import annotations

from lakehouse.core.exceptions import ValidationError
from lakehouse.core.logging import get_logger
from lakehouse.core.spark import get_spark
from lakehouse.ingestion.writers.delta_writer import DeltaWriter
from lakehouse.silver.transformations import (
    cast_types,
    clean_strings,
    drop_invalid_rows,
    enrich,
    normalize_columns,
)

logger = get_logger(__name__)


class SilverProcessor:
    def __init__(self, writer: DeltaWriter | None = None) -> None:
        self.writer = writer or DeltaWriter()

    def run(self, bronze_path: str, silver_path: str) -> None:
        spark = get_spark()
        logger.info("silver.started", bronze_path=bronze_path)

        df = spark.read.format("delta").load(bronze_path)
        df = normalize_columns(df)
        df = clean_strings(df)
        df = cast_types(df)
        df = enrich(df)
        df = drop_invalid_rows(df)

        self._validate(df)

        self.writer.write(df=df, path=silver_path)

        logger.info(
            "silver.completed",
            rows=df.count(),
            columns=len(df.columns),
            silver_path=silver_path,
        )

    def _validate(self, df: "pyspark.sql.DataFrame") -> None:  # type: ignore[name-defined]
        from pyspark.sql import functions as F

        if df.count() == 0:
            raise ValidationError("Silver resultou em DataFrame vazio.")

        required = ["sigla_agente", "sigla_indicador", "ano", "periodo", "valor_indicador"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValidationError(f"Colunas obrigatórias ausentes na Silver: {missing}")

        if df.filter(F.col("periodo") < 1).count() > 0 or df.filter(F.col("periodo") > 12).count() > 0:
            raise ValidationError("Registros com periodo fora do intervalo 1..12.")

        if df.filter(F.col("valor_indicador") < 0).count() > 0:
            raise ValidationError("Registros com valor_indicador negativo.")
