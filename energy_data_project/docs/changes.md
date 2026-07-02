# Changelog — Energy Data Project

Todas as mudanças relevantes do projeto são documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [0.2.0] — 2026-05-07 — `sprint3`

### Adicionado
- **Camada Gold** (`src/energy_data/gold/processor.py`): transforma Silver em modelo analítico com pivot de DEC/FEC, gerando colunas `dec` e `fec` por `(sigla_agente, id_conjunto, nome_conjunto, ano, mes)`. Cria `ano_mes` e `data_referencia`.
- **Validadores Gold** (`src/energy_data/gold/validators.py`): checagens de colunas obrigatórias e tipos na camada Gold.
- **Dashboard Streamlit** (`app/dashboard.py`): visualização interativa da camada Gold com série temporal, ranking por distribuidora, histograma e tabela de preview. Filtros por distribuidora, ano e conjunto via sidebar.
- **Subcomandos CLI** `silver` e `gold`: CLI agora expõe os três estágios do pipeline como subcomandos (`ingest`, `silver`, `gold`) com argumentos de path configuráveis.
- **Testes Gold**: `tests/gold/test_gold_processor.py` e `tests/gold/test_gold_validators.py`.

### Alterado
- `src/energy_data/cli.py`: adicionados subcomandos `silver` e `gold`; funções `run_silver` e `run_gold` extraídas como helpers.
- `README.md`: expandido com instruções completas de execução de cada camada, dashboard e testes.
- `.gitignore`: atualizado com padrões adicionais.

---

## [0.1.0] — 2026-03-24 — `add files energy data project`

### Adicionado
- **Estrutura do projeto**: `src/` layout, `pyproject.toml` com entry point `energy-data`, dependências (Polars, Pydantic, PyYAML, requests, structlog).
- **Core** (`src/energy_data/core/`):
  - `config.py`: modelos Pydantic (`DatasetConfig`, `AppConfig`) e `load_config()` para `configs/datasets.yml`
  - `exceptions.py`: hierarquia `ProjectError → ConfigurationError / IngestionError / ValidationError`
  - `logging.py`: setup de `structlog` com log estruturado em JSON
  - `utils.py`: `sha256_bytes()` para fingerprinting de arquivos
- **Ingestão Bronze** (`src/energy_data/ingestion/`):
  - `HttpFetcher`: download via `requests` com timeout e tratamento de erro HTTP
  - `CsvReader`: leitura de CSV em memória com Polars, suporte a encoding e separador configuráveis
  - `LocalFileWriter`: escrita de bytes no filesystem, criando diretórios intermediários
  - `ParquetWriter`: escrita de `pl.DataFrame` em parquet via PyArrow
  - `IngestionOrchestrator`: compõe todos os componentes e executa o fluxo ponta a ponta
  - `validate_not_empty`, `validate_required_columns`: validações mínimas pós-parse
  - `save_metadata()`: persiste JSON de auditoria em `data/audit/`
  - `IngestionMetadata`: modelo Pydantic do registro de auditoria
- **Silver** (`src/energy_data/silver/`):
  - `transformations.py`: `normalize_columns`, `clean_strings`, `cast_types`, `enrich`, `drop_invalid_rows`
  - `validators.py`: `validate_silver()` com 5 regras de qualidade
  - `SilverProcessor`: orquestra as transformações e validações
  - `SilverWriter`: escreve parquet Silver
- **Bronze contracts**: `src/energy_data/bronze/contracts.py` (placeholder para validações de schema Bronze)
- **CLI** (`src/energy_data/cli.py`): subcomando `ingest` com `--dataset` e `--config`
- **Configuração** (`configs/datasets.yml`): dataset `indicadores_aneel` com URL, opções CSV e paths de saída
- **Testes**: estrutura de diretórios `tests/unit/`, `tests/integration/`, `tests/data_quality/`; `test_config.py`
- **bootstrap_project.py**: script de scaffolding do projeto

---

## [0.0.1] — 2026-03-23 — `first commit`

### Adicionado
- Repositório inicializado com `README.md` vazio.
