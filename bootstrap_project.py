from __future__ import annotations

from pathlib import Path
from textwrap import dedent


PROJECT_NAME = "energy_data_project"


FILES: dict[str, str] = {
    "README.md": dedent(
        """
        # Energy Data Project

        Projeto de Engenharia de Dados para monitoramento da qualidade do fornecimento
        de energia no Brasil com dados públicos da ANEEL.

        ## Objetivo da Sprint 1
        - Definir arquitetura inicial
        - Estruturar projeto
        - Preparar camada de ingestão Bronze
        - Configurar observabilidade básica
        """
    ).strip()
    + "\n",
    "pyproject.toml": dedent(
        """
        [project]
        name = "energy-data-project"
        version = "0.1.0"
        description = "Pipeline de dados para indicadores de continuidade da ANEEL"
        readme = "README.md"
        requires-python = ">=3.11"
        dependencies = [
            "polars>=1.8.0",
            "pydantic>=2.8.0",
            "pyyaml>=6.0.2",
            "requests>=2.32.3",
            "structlog>=24.4.0",
            "duckdb>=1.1.0",
        ]

        [project.optional-dependencies]
        dev = [
            "pytest>=8.3.2",
            "ruff>=0.6.9",
            "mypy>=1.11.2",
        ]

        [project.scripts]
        energy-data = "src.energy_data.cli:main"

        [tool.ruff]
        line-length = 100
        target-version = "py311"

        [tool.mypy]
        python_version = "3.11"
        strict = true
        """
    ).strip()
    + "\n",
    "configs/datasets.yml": dedent(
        """
        datasets:
          indicadores_aneel:
            name: "indicadores_aneel"
            source_type: "http"
            url: "https://dadosabertos.aneel.gov.br/dataset/d5f0712e-62f6-4736-8dff-9991f10758a7/resource/4493985c-baea-429c-9df5-3030422c71d7/download/indicadores-continuidade-coletivos-2020-2029.csv"
            format: "csv"
            load_strategy: "full_refresh"
            partition_by:
              - "ano"
            csv_options:
              separator: ","
              encoding: "utf8"
            required_columns: []
            bronze_path: "data/bronze/aneel/indicadores_aneel"
            raw_path: "data/raw/aneel/indicadores_aneel"
        """
    ).strip()
    + "\n",
    "configs/logging.yml": dedent(
        """
        version: 1
        disable_existing_loggers: false
        """
    ).strip()
    + "\n",
    "src/energy_data/__init__.py": '"""Pacote principal do projeto."""\n',
    "src/energy_data/cli.py": dedent(
        '''
        from __future__ import annotations

        import argparse

        from src.energy_data.core.logging import get_logger


        logger = get_logger(__name__)


        def main() -> None:
            """Ponto de entrada do CLI do projeto."""
            parser = argparse.ArgumentParser(
                prog="energy-data",
                description="CLI do projeto de engenharia de dados de energia."
            )
            parser.add_argument(
                "--dataset",
                type=str,
                required=False,
                help="Nome do dataset a ser processado."
            )

            args = parser.parse_args()
            logger.info("cli.started", dataset=args.dataset)
            print(f"Projeto inicializado. Dataset informado: {args.dataset}")
        '''
    ).strip()
    + "\n",
    "src/energy_data/core/__init__.py": "",
    "src/energy_data/core/config.py": dedent(
        '''
        from __future__ import annotations

        from pathlib import Path
        from typing import Any

        import yaml
        from pydantic import BaseModel, Field


        class CsvOptions(BaseModel):
            """Opções de leitura de arquivos CSV."""

            separator: str = ","
            encoding: str = "utf8"


        class DatasetConfig(BaseModel):
            """Contrato de configuração de um dataset."""

            name: str
            source_type: str
            url: str
            format: str
            load_strategy: str
            partition_by: list[str] = Field(default_factory=list)
            csv_options: CsvOptions = Field(default_factory=CsvOptions)
            required_columns: list[str] = Field(default_factory=list)
            bronze_path: str
            raw_path: str


        class AppConfig(BaseModel):
            """Contrato do arquivo de configuração principal."""

            datasets: dict[str, DatasetConfig]


        def load_config(config_path: str | Path) -> AppConfig:
            """Carrega o arquivo YAML e converte para modelo tipado."""
            path = Path(config_path)
            with path.open("r", encoding="utf-8") as file:
                data: dict[str, Any] = yaml.safe_load(file)

            return AppConfig(**data)
        '''
    ).strip()
    + "\n",
    "src/energy_data/core/logging.py": dedent(
        '''
        from __future__ import annotations

        import logging
        import sys

        import structlog


        def configure_logging() -> None:
            """Configura logging estruturado para o projeto."""
            logging.basicConfig(
                format="%(message)s",
                stream=sys.stdout,
                level=logging.INFO,
            )

            structlog.configure(
                processors=[
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.add_log_level,
                    structlog.processors.JSONRenderer(),
                ],
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )


        def get_logger(name: str):
            """Retorna logger configurado."""
            configure_logging()
            return structlog.get_logger(name)
        '''
    ).strip()
    + "\n",
    "src/energy_data/core/exceptions.py": dedent(
        '''
        class ProjectError(Exception):
            """Exceção base do projeto."""


        class ConfigurationError(ProjectError):
            """Erro de configuração."""


        class IngestionError(ProjectError):
            """Erro de ingestão."""
        '''
    ).strip()
    + "\n",
    "src/energy_data/core/utils.py": dedent(
        '''
        from __future__ import annotations

        import hashlib


        def sha256_bytes(content: bytes) -> str:
            """Gera hash SHA-256 de um conteúdo binário."""
            return hashlib.sha256(content).hexdigest()
        '''
    ).strip()
    + "\n",
    "src/energy_data/ingestion/__init__.py": "",
    "src/energy_data/ingestion/models.py": dedent(
        '''
        from __future__ import annotations

        from dataclasses import dataclass
        from datetime import datetime


        @dataclass(slots=True)
        class IngestionMetadata:
            """Metadados técnicos da execução da ingestão."""

            dataset_name: str
            source: str
            ingestion_timestamp: datetime
            file_hash: str
            row_count: int
            raw_path: str
            bronze_path: str
        '''
    ).strip()
    + "\n",
    "src/energy_data/ingestion/orchestrator.py": dedent(
        '''
        from __future__ import annotations

        from datetime import datetime
        from pathlib import Path

        import polars as pl

        from src.energy_data.core.config import DatasetConfig
        from src.energy_data.core.logging import get_logger
        from src.energy_data.core.utils import sha256_bytes
        from src.energy_data.ingestion.audit.metadata import save_metadata
        from src.energy_data.ingestion.fetchers.http import HttpFetcher
        from src.energy_data.ingestion.models import IngestionMetadata
        from src.energy_data.ingestion.readers.csv_reader import CsvReader
        from src.energy_data.ingestion.writers.local import LocalFileWriter
        from src.energy_data.ingestion.writers.parquet_writer import ParquetWriter


        logger = get_logger(__name__)


        class IngestionOrchestrator:
            """Orquestra o fluxo de ingestão Bronze."""

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
                Executa a ingestão completa.

                Etapas:
                1. Download do arquivo
                2. Armazenamento raw
                3. Leitura estruturada
                4. Enriquecimento técnico
                5. Escrita em parquet
                6. Persistência de metadados
                """
                logger.info("ingestion.started", dataset=dataset.name, source=dataset.url)

                content = self.fetcher.fetch(dataset.url)
                file_hash = sha256_bytes(content)

                raw_path = Path(dataset.raw_path) / "source_file.csv"
                self.raw_writer.write_bytes(content=content, path=raw_path)

                df = self.reader.read(
                    content=content,
                    separator=dataset.csv_options.separator,
                )

                df = self._enrich(df=df, dataset_name=dataset.name, source=dataset.url, file_hash=file_hash)

                bronze_path = Path(dataset.bronze_path) / "dataset.parquet"
                self.parquet_writer.write(df=df, path=bronze_path)

                metadata = IngestionMetadata(
                    dataset_name=dataset.name,
                    source=dataset.url,
                    ingestion_timestamp=datetime.utcnow(),
                    file_hash=file_hash,
                    row_count=df.height,
                    raw_path=str(raw_path),
                    bronze_path=str(bronze_path),
                )

                save_metadata(metadata=metadata, output_dir=Path("data/audit"))
                logger.info("ingestion.completed", dataset=dataset.name, rows=df.height)

                return metadata

            def _enrich(
                self,
                df: pl.DataFrame,
                dataset_name: str,
                source: str,
                file_hash: str,
            ) -> pl.DataFrame:
                """Adiciona colunas técnicas para rastreabilidade."""
                return df.with_row_count("row_number").with_columns(
                    [
                        pl.lit(dataset_name).alias("dataset"),
                        pl.lit(source).alias("source"),
                        pl.lit(file_hash).alias("file_hash"),
                        pl.lit(datetime.utcnow()).alias("ingestion_timestamp"),
                    ]
                )
        '''
    ).strip()
    + "\n",
    "src/energy_data/ingestion/fetchers/__init__.py": "",
    "src/energy_data/ingestion/fetchers/base.py": dedent(
        '''
        from __future__ import annotations

        from typing import Protocol


        class Fetcher(Protocol):
            """Contrato para componentes de extração."""

            def fetch(self, source: str) -> bytes:
                """Obtém conteúdo bruto da fonte."""
                ...
        '''
    ).strip()
    + "\n",
    "src/energy_data/ingestion/fetchers/http.py": dedent(
        '''
        from __future__ import annotations

        import requests


        class HttpFetcher:
            """Extrai conteúdo bruto via HTTP."""

            def fetch(self, source: str) -> bytes:
                response = requests.get(source, timeout=120)
                response.raise_for_status()
                return response.content
        '''
    ).strip()
    + "\n",
    "src/energy_data/ingestion/readers/__init__.py": "",
    "src/energy_data/ingestion/readers/csv_reader.py": dedent(
        '''
        from __future__ import annotations

        from io import BytesIO

        import polars as pl


        class CsvReader:
            """Lê conteúdo CSV em memória e retorna DataFrame Polars."""

            def read(self, content: bytes, separator: str = ",") -> pl.DataFrame:
                return pl.read_csv(
                    BytesIO(content),
                    separator=separator,
                    ignore_errors=False,
                )
        '''
    ).strip()
    + "\n",
    "src/energy_data/ingestion/writers/__init__.py": "",
    "src/energy_data/ingestion/writers/local.py": dedent(
        '''
        from __future__ import annotations

        from pathlib import Path


        class LocalFileWriter:
            """Escreve arquivos binários no disco local."""

            def write_bytes(self, content: bytes, path: str | Path) -> None:
                target = Path(path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
        '''
    ).strip()
    + "\n",
    "src/energy_data/ingestion/writers/parquet_writer.py": dedent(
        '''
        from __future__ import annotations

        from pathlib import Path

        import polars as pl


        class ParquetWriter:
            """Escreve DataFrames em formato Parquet."""

            def write(self, df: pl.DataFrame, path: str | Path) -> None:
                target = Path(path)
                target.parent.mkdir(parents=True, exist_ok=True)
                df.write_parquet(target)
        '''
    ).strip()
    + "\n",
    "src/energy_data/ingestion/audit/__init__.py": "",
    "src/energy_data/ingestion/audit/metadata.py": dedent(
        '''
        from __future__ import annotations

        import json
        from pathlib import Path
        from dataclasses import asdict

        from src.energy_data.ingestion.models import IngestionMetadata


        def save_metadata(metadata: IngestionMetadata, output_dir: Path) -> None:
            """Salva metadados da execução em JSON."""
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{metadata.dataset_name}_metadata.json"

            payload = asdict(metadata)
            payload["ingestion_timestamp"] = metadata.ingestion_timestamp.isoformat()

            output_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        '''
    ).strip()
    + "\n",
    "src/energy_data/bronze/__init__.py": "",
    "src/energy_data/bronze/contracts.py": dedent(
        '''
        """Contratos e regras específicas da camada Bronze."""
        '''
    ).strip()
    + "\n",
    "src/energy_data/silver/__init__.py": "",
    "src/energy_data/gold/__init__.py": "",
    "tests/__init__.py": "",
    "tests/unit/__init__.py": "",
    "tests/integration/__init__.py": "",
    "tests/data_quality/__init__.py": "",
    "tests/unit/test_config.py": dedent(
        '''
        from src.energy_data.core.config import load_config


        def test_load_config() -> None:
            config = load_config("configs/datasets.yml")
            assert "indicadores_aneel" in config.datasets
        '''
    ).strip()
    + "\n",
    "data/raw/.gitkeep": "",
    "data/bronze/.gitkeep": "",
    "data/silver/.gitkeep": "",
    "data/gold/.gitkeep": "",
    "data/audit/.gitkeep": "",
    "docs/.gitkeep": "",
}


def write_file(base_path: Path, relative_path: str, content: str) -> None:
    """Cria diretórios e escreve o conteúdo do arquivo."""
    file_path = base_path / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def create_project_structure(base_dir: str = PROJECT_NAME) -> Path:
    """Cria a estrutura completa do projeto."""
    root = Path(base_dir)
    root.mkdir(parents=True, exist_ok=True)

    for relative_path, content in FILES.items():
        write_file(root, relative_path, content)

    return root


def main() -> None:
    """Executa a criação do scaffold do projeto."""
    project_root = create_project_structure()
    print(f"Estrutura criada com sucesso em: {project_root.resolve()}")


if __name__ == "__main__":
    main()