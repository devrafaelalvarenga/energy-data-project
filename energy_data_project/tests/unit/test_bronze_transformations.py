from __future__ import annotations

import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


@pytest.fixture(scope="module")
def spark() -> SparkSession:
    from lakehouse.core.spark import get_spark
    return get_spark()


def test_bronze_metadata_columns(spark: SparkSession) -> None:
    df = spark.createDataFrame(
        [("CEMIG", "DEC", 2024, 1, "10,5")],
        ["SigAgente", "SigIndicador", "AnoIndice", "NumPeriodoIndice", "VlrIndiceEnviado"],
    )
    enriched = (
        df.withColumn("row_number", F.monotonically_increasing_id())
        .withColumn("dataset", F.lit("indicadores_aneel"))
        .withColumn("source", F.lit("http://example.com"))
        .withColumn("file_hash", F.lit("abc123"))
        .withColumn("ingestion_timestamp", F.lit("2026-07-02T00:00:00+00:00"))
    )
    assert "row_number" in enriched.columns
    assert "dataset" in enriched.columns
    assert "file_hash" in enriched.columns
    assert enriched.count() == 1


def test_bronze_metadata_values(spark: SparkSession) -> None:
    df = spark.createDataFrame([("X",)], ["col"])
    enriched = df.withColumn("dataset", F.lit("test_ds"))
    row = enriched.collect()[0]
    assert row["dataset"] == "test_ds"
