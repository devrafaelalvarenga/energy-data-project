from __future__ import annotations

import polars as pl

from energy_data.core.exceptions import ValidationError


def validate_silver(df: pl.DataFrame) -> None:
    """Aplica validações mínimas de qualidade para a camada Silver."""
    if df.height == 0:
        raise ValidationError("A camada Silver resultou em DataFrame vazio.")

    required = ["sigla_agente", "sigla_indicador", "ano", "periodo", "valor_indicador"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValidationError(f"Colunas obrigatórias ausentes na Silver: {missing}")

    if df.filter(pl.col("sigla_agente").is_null() | (pl.col("sigla_agente") == "")).height > 0:
        raise ValidationError("Existem registros com sigla_agente nula ou vazia.")

    if df.filter(pl.col("sigla_indicador").is_null() | (pl.col("sigla_indicador") == "")).height > 0:
        raise ValidationError("Existem registros com sigla_indicador nula ou vazia.")

    if df.filter((pl.col("periodo") < 1) | (pl.col("periodo") > 12)).height > 0:
        raise ValidationError("Existem registros com periodo fora do intervalo 1..12.")

    if df.filter(pl.col("valor_indicador") < 0).height > 0:
        raise ValidationError("Existem registros com valor_indicador negativo.")