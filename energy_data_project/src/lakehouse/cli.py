from __future__ import annotations

import argparse
import sys

from lakehouse.core.config import load_config
from lakehouse.core.exceptions import LakehouseError
from lakehouse.core.logging import get_logger

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lakehouse",
        description="Modern Energy Lakehouse — CLI do pipeline de dados.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_p = subparsers.add_parser("ingest", help="Ingestão Bronze via PySpark + Delta Lake.")
    ingest_p.add_argument("--dataset", required=True, help="Nome do dataset em configs/datasets.yml")
    ingest_p.add_argument("--config", default="configs/datasets.yml")

    silver_p = subparsers.add_parser("silver", help="Processa Bronze → Silver (PySpark + Delta Lake).")
    silver_p.add_argument("--bronze-path", default="data/bronze/aneel/indicadores_aneel")
    silver_p.add_argument("--silver-path", default="data/silver/aneel/indicadores_aneel")

    gold_p = subparsers.add_parser("gold", help="Processa Silver → Gold via DuckDB.")
    gold_p.add_argument("--silver-path", default="data/silver/aneel/indicadores_aneel")
    gold_p.add_argument("--gold-db-path", default="data/gold/lakehouse.duckdb")

    return parser


def run_ingest(dataset_name: str, config_path: str) -> None:
    from lakehouse.bronze.processor import BronzeProcessor

    config = load_config(config_path)
    if dataset_name not in config.datasets:
        raise LakehouseError(f"Dataset não encontrado: {dataset_name}")

    metadata = BronzeProcessor().run(config.datasets[dataset_name])
    print(f"Ingestão concluída — {metadata.row_count} linhas em {metadata.bronze_path}")


def run_silver(bronze_path: str, silver_path: str) -> None:
    from lakehouse.silver.processor import SilverProcessor

    SilverProcessor().run(bronze_path=bronze_path, silver_path=silver_path)
    print(f"Silver gerada em {silver_path}")


def run_gold(silver_path: str, gold_db_path: str) -> None:
    from lakehouse.gold.processor import GoldProcessor

    row_count = GoldProcessor().run(silver_path=silver_path, gold_db_path=gold_db_path)
    print(f"Gold gerada em {gold_db_path} — {row_count} linhas.")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "ingest":
            run_ingest(args.dataset, args.config)
        elif args.command == "silver":
            run_silver(args.bronze_path, args.silver_path)
        elif args.command == "gold":
            run_gold(args.silver_path, args.gold_db_path)
    except LakehouseError as exc:
        logger.error("cli.error", error=str(exc))
        print(f"Erro: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        logger.exception("cli.unexpected_error", error=str(exc))
        print(f"Erro inesperado: {exc}", file=sys.stderr)
        sys.exit(1)
