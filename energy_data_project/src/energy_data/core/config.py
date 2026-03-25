from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, HttpUrl

from energy_data.core.exceptions import ConfigurationError


class CsvOptions(BaseModel):
    """Opções de leitura de arquivos CSV."""

    separator: str = ";"
    encoding: str = "latin-1"
    infer_schema_length: int = 1000


class DatasetConfig(BaseModel):
    """Contrato de configuração de um dataset."""

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


class AppConfig(BaseModel):
    """Contrato do arquivo principal de configuração."""

    datasets: dict[str, DatasetConfig]


def load_config(config_path: str | Path) -> AppConfig:
    """Carrega e valida o arquivo YAML de configuração."""
    path = Path(config_path)

    if not path.exists():
        raise ConfigurationError(f"Arquivo de configuração não encontrado: {path}")

    with path.open("r", encoding="latin-1") as file:
        data: dict[str, Any] = yaml.safe_load(file)

    return AppConfig(**data)