from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from lakehouse.core.utils import ensure_directory
from lakehouse.ingestion.models import IngestionMetadata


def save_metadata(metadata: IngestionMetadata, output_dir: Path) -> Path:
    ensure_directory(output_dir)
    data = asdict(metadata)
    data["ingestion_timestamp"] = metadata.ingestion_timestamp.isoformat()
    path = output_dir / f"{metadata.dataset_name}_metadata.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return path
