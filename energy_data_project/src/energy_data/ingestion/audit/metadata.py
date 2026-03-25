from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from energy_data.ingestion.models import IngestionMetadata


def save_metadata(metadata: IngestionMetadata, output_dir: Path) -> Path:
    """Salva metadados da execução em arquivo JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{metadata.dataset_name}_metadata.json"
    payload = asdict(metadata)
    payload["ingestion_timestamp"] = metadata.ingestion_timestamp.isoformat()

    output_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_file