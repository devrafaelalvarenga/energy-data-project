from __future__ import annotations

from lakehouse.core.config import DatasetConfig
from lakehouse.core.logging import get_logger
from lakehouse.core.spark import get_spark
from lakehouse.core.utils import sha256_bytes
from lakehouse.ingestion.fetchers.http import HttpFetcher
from lakehouse.ingestion.orchestrator import IngestionOrchestrator
from lakehouse.ingestion.readers.csv_reader import SparkCsvReader
from lakehouse.ingestion.writers.delta_writer import DeltaWriter
from lakehouse.ingestion.writers.local import LocalFileWriter
from lakehouse.ingestion.models import IngestionMetadata

logger = get_logger(__name__)


class BronzeProcessor:
    """Ponto de entrada para a ingestão Bronze: compõe os componentes e delega ao orquestrador."""

    def run(self, dataset: DatasetConfig) -> IngestionMetadata:
        spark = get_spark()
        orchestrator = IngestionOrchestrator(
            fetcher=HttpFetcher(),
            reader=SparkCsvReader(spark),
            raw_writer=LocalFileWriter(),
            delta_writer=DeltaWriter(),
        )
        return orchestrator.run(dataset)
