from __future__ import annotations

import argparse
import sys

from energy_data.core.config import load_config
from energy_data.core.exceptions import ProjectError
from energy_data.core.logging import get_logger
from energy_data.ingestion.fetchers.http import HttpFetcher
from energy_data.ingestion.orchestrator import IngestionOrchestrator
from energy_data.ingestion.readers.csv_reader import CsvReader
from energy_data.ingestion.writers.local import LocalFileWriter
from energy_data.ingestion.writers.parquet_writer import ParquetWriter

from energy_data.silver.processor import SilverProcessor
from energy_data.silver.writer import SilverWriter

from energy_data.gold.processor import GoldProcessor


logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser do CLI."""
    parser = argparse.ArgumentParser(
        prog="energy-data",
        description="CLI do projeto de engenharia de dados de energia.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Executa a ingestão de um dataset configurado.",
    )
    ingest_parser.add_argument(
        "--dataset",
        required=True,
        type=str,
        help="Nome do dataset definido em configs/datasets.yml",
    )
    ingest_parser.add_argument(
        "--config",
        required=False,
        default="configs/datasets.yml",
        type=str,
        help="Caminho para o arquivo de configuração YAML.",
    )
    silver_parser = subparsers.add_parser(
        "silver",
        help="Processa a camada Bronze e gera a camada Silver.",
    )
    silver_parser.add_argument(
        "--bronze-path",
        required=False,
        default="data/bronze/aneel/indicadores_aneel/dataset.parquet",
        type=str,
        help="Caminho do parquet Bronze.",
    )
    silver_parser.add_argument(
        "--silver-path",
        required=False,
        default="data/silver/aneel/indicadores_aneel/dataset.parquet",
        type=str,
        help="Caminho de saída do parquet Silver.",
    )
    gold_parser = subparsers.add_parser("gold", help="Processa camada Gold")
    gold_parser.add_argument(
        "--silver-path",
        default="data/silver/aneel/indicadores_aneel/dataset.parquet"
    )
    gold_parser.add_argument(
        "--gold-path",
        default="data/gold/aneel/indicadores_gold.parquet"
    )
    return parser


def run_ingestion(dataset_name: str, config_path: str) -> None:
    """Executa a ingestão de um dataset a partir do nome configurado."""
    config = load_config(config_path)

    if dataset_name not in config.datasets:
        raise ProjectError(f"Dataset não encontrado na configuração: {dataset_name}")

    dataset = config.datasets[dataset_name]

    orchestrator = IngestionOrchestrator(
        fetcher=HttpFetcher(),
        reader=CsvReader(),
        raw_writer=LocalFileWriter(),
        parquet_writer=ParquetWriter(),
    )

    metadata = orchestrator.run(dataset)

    print("Ingestão concluída com sucesso.")
    print(f"Dataset: {metadata.dataset_name}")
    print(f"Linhas: {metadata.row_count}")
    print(f"Colunas: {metadata.column_count}")
    print(f"Raw: {metadata.raw_path}")
    print(f"Bronze: {metadata.bronze_path}")

def run_silver(bronze_path: str, silver_path: str) -> None:
    processor = SilverProcessor(writer=SilverWriter())
    processor.run(bronze_path=bronze_path, silver_path=silver_path)

    print("Camada Silver gerada com sucesso.")
    print(f"Bronze: {bronze_path}")
    print(f"Silver: {silver_path}")

def run_gold(silver_path: str, gold_path: str) -> None:
    processor = GoldProcessor()
    processor.run(silver_path=silver_path, gold_path=gold_path)

def main() -> None:
    """Ponto de entrada do CLI."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "ingest":
            run_ingestion(dataset_name=args.dataset, config_path=args.config)
    except ProjectError as exc:
        logger.error("application.failed", error=str(exc))
        print(f"Erro: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        logger.exception("application.unexpected_error", error=str(exc))
        print(f"Erro inesperado: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.command == "ingest":
        run_ingestion(dataset_name=args.dataset, config_path=args.config)
    elif args.command == "silver":
        run_silver(bronze_path=args.bronze_path, silver_path=args.silver_path)        
    elif args.command == "gold":
        run_gold(silver_path=args.silver_path, gold_path=args.gold_path)        