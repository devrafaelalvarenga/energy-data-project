from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from energy_data.core.config import DatasetConfig
from energy_data.core.logging import get_logger
from energy_data.core.utils import sha256_bytes
from energy_data.ingestion.audit.metadata import save_metadata
from energy_data.ingestion.fetchers.http import HttpFetcher
from energy_data.ingestion.models import IngestionMetadata
from energy_data.ingestion.readers.csv_reader import CsvReader
from energy_data.ingestion.writers.local import LocalFileWriter
from energy_data.ingestion.writers.parquet_writer import ParquetWriter
from energy_data.ingestion.validators.dataframe import (
    validate_not_empty,
    validate_required_columns,
)

logger = get_logger(__name__)


class IngestionOrchestrator:
    """Orquestra o fluxo de ingestão Bronze ponta a ponta."""

    def __init__(
        self,
        fetcher: HttpFetcher,
        reader: CsvReader,
        raw_writer: LocalFileWriter,
        parquet_writer: ParquetWriter,
    ) -> None:
        self.fetcher = fetcher
        self.reader = reader
        self.raw_writer = raw_writer
        self.parquet_writer = parquet_writer

    def run(self, dataset: DatasetConfig) -> IngestionMetadata:
        """
        Executa a ingestão do dataset configurado.

        Etapas:
            1. Download do arquivo
            2. Escrita raw
            3. Parsing CSV
            4. Validações mínimas
            5. Enriquecimento técnico
            6. Escrita parquet
            7. Persistência de auditoria
        """
        logger.info(
            "ingestion.started",
            dataset=dataset.name,
            source=str(dataset.url),
            strategy=dataset.load_strategy,
        )

        content = self.fetcher.fetch(str(dataset.url))
        file_hash = sha256_bytes(content)

        raw_path = Path(dataset.raw_path) / "source_file.csv"
        self.raw_writer.write_bytes(content=content, path=raw_path)

        df = self.reader.read(
            content=content,
            separator=dataset.csv_options.separator,
            encoding=dataset.csv_options.encoding,
            infer_schema_length=dataset.csv_options.infer_schema_length,
        )

        validate_not_empty(df)
        validate_required_columns(df, dataset.required_columns)

        enriched_df = self._enrich(
            df=df,
            dataset_name=dataset.name,
            source=str(dataset.url),
            file_hash=file_hash,
        )

        bronze_path = Path(dataset.bronze_path) / "dataset.parquet"
        self.parquet_writer.write(df=enriched_df, path=bronze_path)

        metadata = IngestionMetadata(
            dataset_name=dataset.name,
            source=str(dataset.url),
            ingestion_timestamp=datetime.now(timezone.utc),
            file_hash=file_hash,
            row_count=enriched_df.height,
            column_count=enriched_df.width,
            raw_path=str(raw_path),
            bronze_path=str(bronze_path),
        )

        metadata_path = save_metadata(metadata=metadata, output_dir=Path("data/audit"))

        logger.info(
            "ingestion.completed",
            dataset=dataset.name,
            row_count=enriched_df.height,
            column_count=enriched_df.width,
            raw_path=str(raw_path),
            bronze_path=str(bronze_path),
            metadata_path=str(metadata_path),
        )

        return metadata

    def _enrich(
        self,
        df: pl.DataFrame,
        dataset_name: str,
        source: str,
        file_hash: str,
    ) -> pl.DataFrame:
        """Adiciona metadados técnicos ao DataFrame."""
        ingestion_timestamp = datetime.now(timezone.utc).isoformat()

        return df.with_row_index("row_number").with_columns(
            [
                pl.lit(dataset_name).alias("dataset"),
                pl.lit(source).alias("source"),
                pl.lit(file_hash).alias("file_hash"),
                pl.lit(ingestion_timestamp).alias("ingestion_timestamp"),
            ]
        )