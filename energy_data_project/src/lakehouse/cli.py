from __future__ import annotations

import argparse
import subprocess
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

    gold_p = subparsers.add_parser("gold", help="Executa modelos Gold via DBT + DuckDB.")
    gold_p.add_argument("--dbt-dir", default="dbt", help="Diretório do projeto DBT.")
    gold_p.add_argument("--select", default=None, help="Filtro de modelos DBT (ex: gold_indicadores).")

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


def run_gold(dbt_dir: str, select: str | None) -> None:
    cmd = ["dbt", "run"]
    if select:
        cmd += ["--select", select]
    result = subprocess.run(cmd, cwd=dbt_dir)
    if result.returncode != 0:
        raise LakehouseError("dbt run falhou.")
    print("Gold gerada via DBT.")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "ingest":
            run_ingest(args.dataset, args.config)
        elif args.command == "silver":
            run_silver(args.bronze_path, args.silver_path)
        elif args.command == "gold":
            run_gold(args.dbt_dir, getattr(args, "select", None))
    except LakehouseError as exc:
        logger.error("cli.error", error=str(exc))
        print(f"Erro: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        logger.exception("cli.unexpected_error", error=str(exc))
        print(f"Erro inesperado: {exc}", file=sys.stderr)
        sys.exit(1)
