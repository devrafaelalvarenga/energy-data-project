from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import functions as F

from lakehouse.core.config import DatasetConfig
from lakehouse.core.logging import get_logger
from lakehouse.core.utils import sha256_bytes
from lakehouse.ingestion.audit.metadata import save_metadata
from lakehouse.ingestion.fetchers.http import HttpFetcher
from lakehouse.ingestion.models import IngestionMetadata
from lakehouse.ingestion.readers.csv_reader import SparkCsvReader
from lakehouse.ingestion.writers.delta_writer import DeltaWriter
from lakehouse.ingestion.writers.local import LocalFileWriter

logger = get_logger(__name__)


class IngestionOrchestrator:
    def __init__(
        self,
        fetcher: HttpFetcher,
        reader: SparkCsvReader,
        raw_writer: LocalFileWriter,
        delta_writer: DeltaWriter,
    ) -> None:
        self.fetcher = fetcher
        self.reader = reader
        self.raw_writer = raw_writer
        self.delta_writer = delta_writer

    def run(self, dataset: DatasetConfig) -> IngestionMetadata:
        logger.info("ingestion.started", dataset=dataset.name, source=str(dataset.url))

        content = self.fetcher.fetch(str(dataset.url))
        file_hash = sha256_bytes(content)

        raw_path = Path(dataset.raw_path) / "source_file.csv"
        self.raw_writer.write_bytes(content=content, path=raw_path)

        df = self.reader.read(
            path=str(raw_path),
            separator=dataset.csv_options.separator,
            encoding=dataset.csv_options.encoding,
        )

        ingestion_ts = datetime.now(timezone.utc).isoformat()
        df = (
            df.withColumn("row_number", F.monotonically_increasing_id())
            .withColumn("dataset", F.lit(dataset.name))
            .withColumn("source", F.lit(str(dataset.url)))
            .withColumn("file_hash", F.lit(file_hash))
            .withColumn("ingestion_timestamp", F.lit(ingestion_ts))
        )

        bronze_path = dataset.bronze_path
        self.delta_writer.write(df=df, path=bronze_path)

        row_count = df.count()
        col_count = len(df.columns)

        metadata = IngestionMetadata(
            dataset_name=dataset.name,
            source=str(dataset.url),
            ingestion_timestamp=datetime.now(timezone.utc),
            file_hash=file_hash,
            row_count=row_count,
            column_count=col_count,
            raw_path=str(raw_path),
            bronze_path=bronze_path,
        )

        save_metadata(metadata=metadata, output_dir=Path("data/audit"))

        logger.info(
            "ingestion.completed",
            dataset=dataset.name,
            row_count=row_count,
            bronze_path=bronze_path,
        )
        return metadata
