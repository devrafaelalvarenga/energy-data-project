# Changelog — Modern Energy Lakehouse

Todas as mudanças relevantes do projeto são documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [0.3.0] — 2026-07-02 — `sprint4 / modern-energy-lakehouse`

### Adicionado
- **Pacote `src/lakehouse/`**: reescrita limpa substituindo `src/energy_data/`. Novo nome reflete o projeto Modern Energy Lakehouse.
- **`core/spark.py`**: factory `get_spark()` que cria SparkSession em modo local com Delta Lake configurado (`delta-spark 3.2.0`, extensão DeltaSparkSessionExtension, DeltaCatalog).
- **`ingestion/readers/csv_reader.py`**: `SparkCsvReader` — lê CSV via `spark.read.csv` com header, sep e encoding configuráveis.
- **`ingestion/writers/delta_writer.py`**: `DeltaWriter` — escreve Spark DataFrame como Delta Lake com `mode("overwrite")` e `overwriteSchema=true`.
- **`bronze/processor.py`**: `BronzeProcessor` — ponto de entrada da camada Bronze, compõe SparkSession + orquestrador.
- **`silver/transformations.py`**: 5 funções reescritas com PySpark Column API: `normalize_columns`, `clean_strings`, `cast_types`, `enrich`, `drop_invalid_rows`.
- **`silver/processor.py`**: `SilverProcessor` reescrito com PySpark; lê Bronze Delta, aplica transformações, valida e escreve Silver Delta.
- **`dbt/`**: projeto DBT completo com `dbt-duckdb`:
  - `dbt_project.yml` — configuração do projeto
  - `profiles.yml` — perfil DuckDB com extensão `delta`
  - `models/gold/gold_indicadores.sql` — pivot DEC/FEC via `delta_scan` + SQL PIVOT
  - `models/gold/schema.yml` — testes `not_null` e `accepted_values`
- **`app/dashboard.py`**: atualizado para ler de `data/gold/lakehouse.duckdb` via `duckdb.connect`. Remove dependência de Polars e parquet no dashboard.
- **`.github/workflows/ci.yml`**: CI com setup Java 17 + Python 3.11, ruff, mypy, pytest com cobertura.
- **`.github/workflows/pipeline.yml`**: pipeline manual (workflow_dispatch) executando ingest → silver → dbt run → dbt test.
- **`tests/unit/test_silver_transformations.py`**: 5 testes das transformações Silver com PySpark local.
- **`tests/unit/test_bronze_transformations.py`**: 2 testes de enriquecimento técnico Bronze.

### Alterado
- **`pyproject.toml`**: nome `modern-energy-lakehouse` v0.3.0; dependências trocadas: remove `polars`, adiciona `pyspark`, `delta-spark`, `duckdb`, `dbt-core`, `dbt-duckdb`, `streamlit`; entry point renomeado para `lakehouse`.
- **`src/lakehouse/cli.py`**: subcomando `gold` agora executa `dbt run` via subprocess. Subcomandos `ingest` e `silver` delegam para `BronzeProcessor` e `SilverProcessor`.
- **`core/exceptions.py`**: exceção base renomeada de `ProjectError` para `LakehouseError`.
- **`configs/datasets.yml`**: compatível com o novo stack sem alterações na estrutura.

### Removido
- **`src/energy_data/`**: pacote inteiro removido após migração.
- **`gold/processor.py`** (Polars): substituído por `dbt/models/gold/gold_indicadores.sql`.
- **`gold/validators.py`** (Polars): tinha bug (comparava nomes maiúsculos vs minúsculos); substituído por DBT tests.
- **`silver/transformations/`** sub-pacote: dead code (não era importado em lugar nenhum).
- **`silver/writer.py`** (Polars): substituído por `DeltaWriter`.
- **`bronze/contracts.py`**: stub vazio removido.

---

## [0.2.0] — 2026-05-07 — `sprint3`

### Adicionado
- Camada Gold (`GoldProcessor`): pivot DEC/FEC, modelo analítico por conjunto/período (Polars)
- Dashboard Streamlit (`app/dashboard.py`): série temporal, ranking, histograma, filtros
- CLI estendido com subcomandos `silver` e `gold`
- Testes Gold: `test_gold_processor.py`, `test_gold_validators.py`
- README expandido

### Alterado
- `src/energy_data/cli.py`: adicionados subcomandos `silver` e `gold`

---

## [0.1.0] — 2026-03-24 — `add files energy data project`

### Adicionado
- Estrutura completa do projeto: `src/` layout, `pyproject.toml`, entry point `energy-data`
- Core: `config.py` (Pydantic), `exceptions.py`, `logging.py` (structlog), `utils.py`
- Ingestão Bronze: `HttpFetcher`, `CsvReader` (Polars), `LocalFileWriter`, `ParquetWriter`, `IngestionOrchestrator`
- Silver: `SilverProcessor`, `transformations.py`, `validators.py`, `SilverWriter` (Polars)
- `configs/datasets.yml` com dataset `indicadores_aneel`
- Testes: `test_config.py`

---

## [0.0.1] — 2026-03-23 — `first commit`

### Adicionado
- Repositório inicializado com README vazio.
