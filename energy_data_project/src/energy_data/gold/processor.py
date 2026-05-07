from __future__ import annotations

from pathlib import Path

import polars as pl

from energy_data.core.logging import get_logger

logger = get_logger(__name__)


class GoldProcessor:
    """Processa a camada Silver e gera a camada Gold."""

    def run(self, silver_path: str, gold_path: str) -> None:
        logger.info("gold.started", silver_path=silver_path)

        df = pl.read_parquet(silver_path)
        df_gold = self._transform(df)

        Path(gold_path).parent.mkdir(parents=True, exist_ok=True)
        df_gold.write_parquet(gold_path)

        logger.info(
            "gold.completed",
            rows=df_gold.height,
            columns=df_gold.width,
            gold_path=gold_path,
        )

    def _transform(self, df: pl.DataFrame) -> pl.DataFrame:
        """Transforma dados da Silver para o modelo analítico Gold."""

        required = [
            "sigla_agente",
            "id_conjunto",
            "nome_conjunto",
            "ano",
            "periodo",
            "sigla_indicador",
            "valor_indicador",
        ]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes na Silver para gerar Gold: {missing}")

        # Padroniza indicador e valor
        df = df.with_columns([
            pl.col("sigla_indicador")
            .cast(pl.Utf8, strict=False)
            .str.strip_chars()
            .str.to_uppercase()
            .alias("sigla_indicador"),

            pl.col("valor_indicador")
            .cast(pl.Float64, strict=False)
            .alias("valor_indicador"),
        ])

        # Mantém só DEC/FEC para a camada analítica principal
        df = df.filter(pl.col("sigla_indicador").is_in(["DEC", "FEC"]))

        # Pivot: DEC/FEC viram colunas
        df_gold = df.pivot(
            values="valor_indicador",
            index=[
                "sigla_agente",
                "id_conjunto",
                "nome_conjunto",
                "ano",
                "periodo",
            ],
            on="sigla_indicador",
            aggregate_function="first",
        )

        # Renomeia para padrão do dashboard
        rename_map = {}
        if "DEC" in df_gold.columns:
            rename_map["DEC"] = "dec"
        if "FEC" in df_gold.columns:
            rename_map["FEC"] = "fec"
        if "periodo" in df_gold.columns:
            rename_map["periodo"] = "mes"

        if rename_map:
            df_gold = df_gold.rename(rename_map)

        # Cria ano_mes e data_referencia
        if "ano" in df_gold.columns and "mes" in df_gold.columns:
            df_gold = df_gold.with_columns([
                (pl.col("ano") * 100 + pl.col("mes")).alias("ano_mes"),
                pl.date(pl.col("ano"), pl.col("mes"), pl.lit(1)).alias("data_referencia"),
            ])

        return df_gold