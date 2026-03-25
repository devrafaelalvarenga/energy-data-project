import polars as pl


def enrich(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns([
        (pl.col("ano") * 100 + pl.col("mes")).alias("ano_mes"),
    ])