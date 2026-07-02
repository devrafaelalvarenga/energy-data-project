from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, HttpUrl

from lakehouse.core.exceptions import ConfigurationError


class CsvOptions(BaseModel):
    separator: str = ";"
    encoding: str = "latin-1"
    infer_schema_length: int = 1000


class DatasetConfig(BaseModel):
    name: str
    source_type: str
    url: HttpUrl
    format: str
    load_strategy: str
    partition_by: list[str] = Field(default_factory=list)
    csv_options: CsvOptions = Field(default_factory=CsvOptions)
    required_columns: list[str] = Field(default_factory=list)
    raw_path: str
    bronze_path: str
    silver_path: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.silver_path:
            self.silver_path = self.bronze_path.replace("bronze", "silver")


class AppConfig(BaseModel):
    datasets: dict[str, DatasetConfig]


def load_config(config_path: str | Path) -> AppConfig:
    path = Path(config_path)
    if not path.exists():
        raise ConfigurationError(f"Arquivo de configuração não encontrado: {path}")
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)
    return AppConfig(**data)
