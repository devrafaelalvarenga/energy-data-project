import polars as pl


def cast_types(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns([
        pl.col("ano").cast(pl.Int64, strict=False),
        pl.col("mes").cast(pl.Int64, strict=False),
        pl.col("dec").cast(pl.Float64, strict=False),
        pl.col("fec").cast(pl.Float64, strict=False),
    ])