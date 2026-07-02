from __future__ import annotations

import pytest
from pyspark.sql import SparkSession

from lakehouse.silver.transformations import (
    cast_types,
    clean_strings,
    drop_invalid_rows,
    enrich,
    normalize_columns,
)


@pytest.fixture(scope="module")
def spark() -> SparkSession:
    from lakehouse.core.spark import get_spark
    return get_spark()


def test_normalize_columns(spark: SparkSession) -> None:
    df = spark.createDataFrame(
        [("CEMIG", "DEC", 2024, 1, "10,5")],
        ["SigAgente", "SigIndicador", "AnoIndice", "NumPeriodoIndice", "VlrIndiceEnviado"],
    )
    result = normalize_columns(df)
    assert "sigla_agente" in result.columns
    assert "sigla_indicador" in result.columns
    assert "SigAgente" not in result.columns


def test_clean_strings_strips_and_nullifies(spark: SparkSession) -> None:
    df = spark.createDataFrame(
        [("  CEMIG  ", ""), (" DEC", None)],
        ["sigla_agente", "sigla_indicador"],
    )
    result = clean_strings(df)
    rows = {r["sigla_agente"]: r["sigla_indicador"] for r in result.collect()}
    assert rows["CEMIG"] is None
    assert rows["DEC"] is None


def test_cast_types_decimal_comma(spark: SparkSession) -> None:
    df = spark.createDataFrame(
        [("CEMIG", "DEC", 2024, 1, "10,50")],
        ["sigla_agente", "sigla_indicador", "ano", "periodo", "valor_indicador"],
    )
    result = cast_types(df)
    row = result.collect()[0]
    assert row["valor_indicador"] == pytest.approx(10.50)
    assert row["ano"] == 2024
    assert row["periodo"] == 1


def test_enrich_creates_ano_mes(spark: SparkSession) -> None:
    df = spark.createDataFrame([(2024, 3)], ["ano", "periodo"])
    result = enrich(df)
    row = result.collect()[0]
    assert row["ano_mes"] == 202403
    assert str(row["data_referencia"]) == "2024-03-01"


def test_drop_invalid_rows_removes_nulls(spark: SparkSession) -> None:
    df = spark.createDataFrame(
        [("CEMIG", "DEC", 2024, 1, 10.5), (None, "FEC", 2024, 2, 5.0)],
        ["sigla_agente", "sigla_indicador", "ano", "periodo", "valor_indicador"],
    )
    result = drop_invalid_rows(df)
    assert result.count() == 1
    assert result.collect()[0]["sigla_agente"] == "CEMIG"
