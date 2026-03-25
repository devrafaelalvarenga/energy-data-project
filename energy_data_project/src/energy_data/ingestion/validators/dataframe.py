from __future__ import annotations

import polars as pl

from energy_data.core.exceptions import ValidationError


def validate_not_empty(df: pl.DataFrame) -> None:
    """Valida se o DataFrame possui linhas."""
    if df.height == 0:
        raise ValidationError("O DataFrame está vazio.")


def validate_required_columns(df: pl.DataFrame, required_columns: list[str]) -> None:
    """Valida se as colunas obrigatórias existem."""
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValidationError(f"Colunas obrigatórias ausentes: {missing}")