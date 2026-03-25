import polars as pl


def clean_column_names(df: pl.DataFrame) -> pl.DataFrame:
    return df.rename({
        col: col.strip().lower().replace(" ", "_")
        for col in df.columns
    })