from __future__ import annotations

from pathlib import Path

import duckdb

from lakehouse.core.logging import get_logger

logger = get_logger(__name__)

_GOLD_SQL = """
WITH base AS (
    SELECT *
    FROM delta_scan('{silver_path}')
    WHERE sigla_indicador IN ('DEC', 'FEC')
),
pivoted AS (
    PIVOT base
    ON sigla_indicador IN ('DEC', 'FEC')
    USING first(valor_indicador)
    GROUP BY sigla_agente, id_conjunto, nome_conjunto, ano, periodo
)
SELECT
    sigla_agente,
    id_conjunto,
    nome_conjunto,
    ano,
    periodo         AS mes,
    "DEC"           AS dec,
    "FEC"           AS fec,
    ano * 100 + periodo         AS ano_mes,
    make_date(ano::INT, periodo::INT, 1)  AS data_referencia
FROM pivoted
"""


class GoldProcessor:
    def run(
        self,
        silver_path: str = "data/silver/aneel/indicadores_aneel",
        gold_db_path: str = "data/gold/lakehouse.duckdb",
    ) -> int:
        Path(gold_db_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info("gold.started", silver_path=silver_path, gold_db_path=gold_db_path)

        con = duckdb.connect(gold_db_path)
        con.execute("INSTALL delta; LOAD delta;")

        sql = _GOLD_SQL.format(silver_path=silver_path)
        con.execute("DROP TABLE IF EXISTS gold_indicadores")
        con.execute(f"CREATE TABLE gold_indicadores AS {sql}")

        row_count = con.execute("SELECT count(*) FROM gold_indicadores").fetchone()[0]
        con.close()

        logger.info("gold.completed", row_count=row_count, gold_db_path=gold_db_path)
        return row_count
