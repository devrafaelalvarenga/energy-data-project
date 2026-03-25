from __future__ import annotations

import polars as pl


def normalize_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Renomeia colunas do schema Bronze para o schema Silver."""
    rename_map = {
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

    existing = {k: v for k, v in rename_map.items() if k in df.columns}
    return df.rename(existing)


def clean_strings(df: pl.DataFrame) -> pl.DataFrame:
    cols = [
        c for c in [
            "sigla_agente",
            "cnpj",
            "id_conjunto",
            "nome_conjunto",
            "sigla_indicador",
        ]
        if c in df.columns
    ]

    exprs: list[pl.Expr] = []
    for col in cols:
        exprs.append(
            pl.col(col)
            .cast(pl.Utf8, strict=False)
            .str.strip_chars()
            .replace("", None)
            .alias(col)
        )

    return df.with_columns(exprs)


def cast_types(df: pl.DataFrame) -> pl.DataFrame:
    """Converte tipos para o schema Silver."""
    exprs: list[pl.Expr] = []

    if "ano" in df.columns:
        exprs.append(pl.col("ano").cast(pl.Int32, strict=False).alias("ano"))

    if "periodo" in df.columns:
        exprs.append(pl.col("periodo").cast(pl.Int8, strict=False).alias("periodo"))

    if "valor_indicador" in df.columns:
        exprs.append(
            pl.col("valor_indicador")
            .cast(pl.Utf8, strict=False)
            .str.replace_all(r"\.", "")     # remove separador de milhar, se vier
            .str.replace(",", ".")          # troca vírgula decimal por ponto
            .cast(pl.Float64, strict=False)
            .alias("valor_indicador")
        )

    if "data_geracao" in df.columns:
        exprs.append(
            pl.col("data_geracao")
            .cast(pl.Utf8, strict=False)
            .str.to_date(strict=False)
            .alias("data_geracao")
        )

    return df.with_columns(exprs)


def enrich(df: pl.DataFrame) -> pl.DataFrame:
    """Cria colunas derivadas úteis para análise."""
    exprs: list[pl.Expr] = []

    if "ano" in df.columns and "periodo" in df.columns:
        exprs.extend(
            [
                (pl.col("ano") * 100 + pl.col("periodo")).alias("ano_mes"),
                pl.date(pl.col("ano"), pl.col("periodo"), pl.lit(1)).alias("data_referencia"),
            ]
        )

    return df.with_columns(exprs)

def drop_invalid_rows(df: pl.DataFrame) -> pl.DataFrame:
    """Remove linhas sem campos mínimos obrigatórios."""
    required = ["sigla_agente", "sigla_indicador", "ano", "periodo", "valor_indicador"]

    existing = [c for c in required if c in df.columns]
    if not existing:
        return df

    condition = None
    for col in existing:
        current = pl.col(col).is_not_null()
        if condition is None:
            condition = current
        else:
            condition = condition & current

    return df.filter(condition)