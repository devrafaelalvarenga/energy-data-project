import polars as pl

from energy_data.core.exceptions import ValidationError


def validate_quality(df: pl.DataFrame) -> None:
    if (df["dec"] < 0).any():
        raise ValidationError("DEC inválido (negativo)")

    if (df["fec"] < 0).any():
        raise ValidationError("FEC inválido (negativo)")