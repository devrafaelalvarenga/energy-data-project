# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
> Este arquivo é o ponto de entrada da IA para este projeto.
> Ele funciona como um índice: não contém detalhes longos — aponta para os documentos certos.
> Toda instrução longa ou técnica vive em docs/. Este arquivo deve permanecer enxuto.

## 🗂️ Índice de Documentos Obrigatórios

> A IA deve ler todos os arquivos abaixo antes de executar qualquer tarefa.

|Arquivo |Descrição |Atualizado em|
|----------------------------|--------------------------------------------------------|-------------|
|`docs/ARQUITETURA.md` |Estrutura de tabelas, funções, triggers e fluxo de dados|02/07/2026 às 00h19 BRT|
|`docs/ROADMAP.md` |Tarefas pendentes, em andamento e concluídas |02/07/2026 às 00h19 BRT|
|`docs/CHANGES.md` |Changelog de todas as alterações relevantes |02/07/2026 às 00h19 BRT|
|`docs/integracoes/README.md`|Índice de todas as integrações externas documentadas |— |

> Regra: toda vez que um arquivo acima for alterado, atualizar imediatamente o campo “Atualizado em” com a data e hora no fuso BRT (ex: `20/03/2025 às 14h32 BRT`).

-----

## 🧠 Como a IA deve se comunicar

- Usar linguagem didática e muito explicada, como se estivesse falando com alguém que não tem experiência em programação
- Explicar cada conceito antes de usá-lo
- Usar analogias do mundo real para simplificar ideias técnicas
- Evitar jargão — quando for inevitável usá-lo, explicar em seguida o que significa
- Ser paciente e claro, assumindo zero conhecimento prévio
- Responder sempre em Português do Brasil

-----

## 📋 Regras Obrigatórias

### Documentação

- [ ] Toda alteração na estrutura de tabelas, funções, triggers ou fluxo de dados → atualizar docs/ARQUITETURA.md
- [ ] Toda etapa concluída ou iniciada → atualizar docs/ROADMAP.md
- [ ] Toda mudança relevante → registrar em docs/CHANGES.md com data e descrição
- [ ] Todo novo documento criado → referenciar no índice deste arquivo com a data
- [ ] Este arquivo (`CLAUDE.md`) deve permanecer enxuto — nunca adicionar conteúdo longo aqui

### Código

- [ ] Proibido cores hardcoded 
- [ ] Tudo precisa ser documentado — funções, componentes, lógicas complexas e decisões de arquitetura
- [ ] Tudo precisa ser testado — 

### Integrações

- [ ] Toda integração com serviço externo deve ser pesquisada na documentação oficial antes de ser implementada
- [ ] Toda integração deve ser documentada dentro de docs/integracoes/ com um arquivo próprio
- [ ] O arquivo docs/integracoes/README.md deve ser atualizado com o índice de integrações

### Ambiente e Infraestrutura

- [ ] Criar e manter o arquivo .env com todas as chaves necessárias já estruturadas e comentadas, deixando os valores em branco para preenchimento manual

-----

## 🧪 Padrão de Testes

- Testes unitários e de integração devem cobrir os fluxos principais
- Casos críticos ou com lógica complexa → testar 

## Setup

All commands must be run from the `energy_data_project/` directory.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Pipeline Commands

```bash
# Ingest ANEEL data → raw/ + bronze/ (parquet)
energy-data ingest --dataset indicadores_aneel

# Bronze → Silver (clean + typed + validated)
energy-data silver

# Silver → Gold (pivot DEC/FEC into columns, add ano_mes + data_referencia)
energy-data gold

# Streamlit dashboard (reads data/gold/aneel/indicadores_gold.parquet)
streamlit run app/dashboard.py
```

## Tests, Lint, Types

```bash
pytest tests/                   # all tests
pytest tests/unit/              # unit only
pytest tests/gold/              # gold layer tests
ruff check src/
mypy src/
```

To run a single test: `pytest tests/unit/test_config.py::test_load_config`

## Architecture

Medallion pipeline: **HTTP (ANEEL CSV) → raw/ → Bronze → Silver → Gold → Streamlit**.

**Data flow per layer:**
- **Bronze** (`IngestionOrchestrator`): downloads CSV, saves raw bytes to `data/raw/`, parses with Polars, appends technical metadata columns (`row_number`, `dataset`, `source`, `file_hash`, `ingestion_timestamp`), writes parquet to `data/bronze/`. Saves JSON audit record to `data/audit/`.
- **Silver** (`SilverProcessor`): reads Bronze parquet → `normalize_columns` (PascalCase → snake_case rename) → `clean_strings` → `cast_types` (handles comma-decimal `valor_indicador`) → `enrich` (adds `ano_mes`, `data_referencia`) → `drop_invalid_rows` → `validate_silver`. Raises `ValidationError` on quality failures.
- **Gold** (`GoldProcessor`): reads Silver → filters to DEC/FEC indicators → `pivot` on `sigla_indicador` so each row has `dec` and `fec` columns → adds `ano_mes` and `data_referencia`. Column `periodo` is renamed to `mes`.

**Key design points:**
- `configs/datasets.yml` is the single source of truth for dataset URLs, CSV options, and output paths. Adding a new dataset means a new entry here plus implementing fetcher/reader interfaces.
- `IngestionOrchestrator` is dependency-injected: `HttpFetcher`, `CsvReader`, `LocalFileWriter`, `ParquetWriter`. Swap implementations without touching orchestration logic.
- Exception hierarchy: `ProjectError` → `ConfigurationError` / `IngestionError` / `ValidationError`. All handled at the CLI boundary in `cli.py::main`.
- `structlog` is used throughout; log events follow `layer.event` naming (e.g. `silver.completed`, `ingestion.started`).
- `mypy` runs in strict mode; `ruff` line-length is 100.

**Source layout:**
```
src/energy_data/
├── cli.py                  # entry point, arg parsing, command dispatch
├── core/                   # config (Pydantic), exceptions, logging, utils
├── ingestion/              # orchestrator, HttpFetcher, CsvReader, writers, validators, audit
├── bronze/                 # contracts.py (placeholder for bronze-layer schemas)
├── silver/                 # SilverProcessor, transformations.py, validators.py, writer.py
└── gold/                   # GoldProcessor, validators.py
```
