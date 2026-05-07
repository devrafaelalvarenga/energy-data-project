import polars as pl
from energy_data.core.exceptions import ValidationError


def validate_gold(df: pl.DataFrame) -> None:
    """
    Valida qualidade dos dados da camada Gold.
    """

    if df.height == 0:
        raise ValidationError("Gold dataset vazio.")

    if df.select(pl.col("DEC").is_null().any()).item():
        raise ValidationError("Existem valores nulos em DEC.")

    if df.select(pl.col("FEC").is_null().any()).item():
        raise ValidationError("Existem valores nulos em FEC.")

    if df.select((pl.col("DEC") < 0).any()).item():
        raise ValidationError("DEC possui valores negativos.")

    if df.select((pl.col("FEC") < 0).any()).item():
        raise ValidationError("FEC possui valores negativos.")