from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, ByteType


RENAME_MAP = {
    "DatGeracaoConjuntoDados": "data_geracao",
    "SigAgente": "sigla_agente",
    "NumCNPJ": "cnpj",
    "IdeConjUndConsumidoras": "id_conjunto",
    "DscConjUndConsumidoras": "nome_conjunto",
    "SigIndicador": "sigla_indicador",
    "AnoIndice": "ano",
    "NumPeriodoIndice": "periodo",
    "VlrIndiceEnviado": "valor_indicador",
}

STRING_COLS = ["sigla_agente", "cnpj", "id_conjunto", "nome_conjunto", "sigla_indicador"]


def normalize_columns(df: DataFrame) -> DataFrame:
    for old, new in RENAME_MAP.items():
        if old in df.columns:
            df = df.withColumnRenamed(old, new)
    return df


def clean_strings(df: DataFrame) -> DataFrame:
    for col in STRING_COLS:
        if col in df.columns:
            df = df.withColumn(
                col,
                F.when(F.trim(F.col(col)) == "", None).otherwise(F.trim(F.col(col))),
            )
    return df


def cast_types(df: DataFrame) -> DataFrame:
    if "ano" in df.columns:
        df = df.withColumn("ano", F.col("ano").cast(IntegerType()))

    if "periodo" in df.columns:
        df = df.withColumn("periodo", F.col("periodo").cast(ByteType()))

    if "valor_indicador" in df.columns:
        df = df.withColumn(
            "valor_indicador",
            F.regexp_replace(F.col("valor_indicador").cast("string"), r"\.", ""),
        )
        df = df.withColumn(
            "valor_indicador",
            F.regexp_replace(F.col("valor_indicador"), ",", ".").cast(DoubleType()),
        )

    if "data_geracao" in df.columns:
        df = df.withColumn("data_geracao", F.to_date(F.col("data_geracao").cast("string")))

    return df


def enrich(df: DataFrame) -> DataFrame:
    if "ano" in df.columns and "periodo" in df.columns:
        df = df.withColumn("ano_mes", F.col("ano") * 100 + F.col("periodo"))
        df = df.withColumn(
            "data_referencia",
            F.to_date(
                F.concat(
                    F.col("ano").cast("string"),
                    F.lit("-"),
                    F.lpad(F.col("periodo").cast("string"), 2, "0"),
                    F.lit("-01"),
                )
            ),
        )
    return df


def drop_invalid_rows(df: DataFrame) -> DataFrame:
    required = ["sigla_agente", "sigla_indicador", "ano", "periodo", "valor_indicador"]
    existing = [c for c in required if c in df.columns]
    return df.dropna(subset=existing)
