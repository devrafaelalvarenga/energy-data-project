from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class IngestionMetadata:
    dataset_name: str
    source: str
    ingestion_timestamp: datetime
    file_hash: str
    row_count: int
    column_count: int
    raw_path: str
    bronze_path: str
