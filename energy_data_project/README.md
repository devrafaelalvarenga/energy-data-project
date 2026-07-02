# Modern Energy Lakehouse

Pipeline de dados em arquitetura Medallion para processamento e análise dos indicadores de continuidade do fornecimento de energia elétrica da ANEEL — construído com PySpark, Delta Lake, DBT e DuckDB.

---

## Arquitetura

```
Fonte CSV (ANEEL)
        ↓
    RAW (bytes)
        ↓ PySpark
   Bronze (Delta Lake)
        ↓ PySpark + Delta Lake
   Silver (Delta Lake)
        ↓ DBT + DuckDB
    Gold (DuckDB)
        ↓ Streamlit
    Dashboard
```

| Camada | Tecnologia | O que faz |
|---|---|---|
| Bronze | PySpark + Delta Lake | Download, parsing CSV, enriquecimento técnico |
| Silver | PySpark + Delta Lake | Limpeza, tipagem, validação de qualidade |
| Gold | DBT + dbt-duckdb | Pivot DEC/FEC, modelo analítico via `delta_scan` |
| Dashboard | Streamlit + DuckDB | Visualização interativa da camada Gold |

---

## Stack

- **Python 3.11+**
- **PySpark 4.x** — processamento distribuído
- **Delta Lake** — formato de armazenamento com ACID e time travel
- **DuckDB** — query engine que lê Delta nativo
- **DBT (dbt-duckdb)** — transformações SQL da camada Gold
- **Streamlit** — dashboard interativo
- **GitHub Actions** — CI (lint + testes) e pipeline (manual dispatch)

---

## Pré-requisitos

- Python 3.11+
- **Java 21** (obrigatório para PySpark 4.x)

```bash
brew install openjdk@21
export JAVA_HOME=/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home
```

---

## Setup

```bash
cd energy_data_project

python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env   # revisar JAVA_HOME se necessário
```

---

## Executando o Pipeline

```bash
# 1. Bronze — download ANEEL + escrita Delta Lake
lakehouse ingest --dataset indicadores_aneel

# 2. Silver — limpeza, tipagem e validação
lakehouse silver

# 3. Gold — modelos DBT via DuckDB
lakehouse gold

# 4. Dashboard
streamlit run app/dashboard.py
```

### DBT diretamente

```bash
cd dbt
dbt run       # executa os modelos Gold
dbt test      # valida qualidade dos dados
```

---

## Testes e Qualidade

```bash
pytest tests/unit/ -v                  # todos os testes unitários
pytest tests/unit/test_silver_transformations.py  # Silver específico
ruff check src/                        # lint
mypy src/lakehouse/                    # type check
```

---

## Estrutura

```
energy_data_project/
├── src/lakehouse/
│   ├── core/          # config, exceptions, logging, spark factory
│   ├── ingestion/     # HttpFetcher, SparkCsvReader, DeltaWriter, orchestrator
│   ├── bronze/        # BronzeProcessor
│   └── silver/        # SilverProcessor + transformações PySpark
├── dbt/
│   ├── models/gold/   # gold_indicadores.sql + schema.yml (DBT tests)
│   └── profiles.yml   # dbt-duckdb + delta extension
├── app/
│   └── dashboard.py   # Streamlit lendo DuckDB
├── tests/
│   └── unit/          # config, bronze, silver
├── configs/
│   └── datasets.yml   # URL, csv_options e paths por dataset
├── docs/              # arquitetura.md, roadmap.md, changes.md, CLAUDE.md
└── .github/workflows/ # ci.yml + pipeline.yml
```

---

## Fonte dos Dados

Dataset público ANEEL — Indicadores de Continuidade Coletivos (2020–2029):
https://dadosabertos.aneel.gov.br/dataset/d5f0712e-62f6-4736-8dff-9991f10758a7/resource/4493985c-baea-429c-9df5-3030422c71d7/download/indicadores-continuidade-coletivos-2020-2029.csv

---

## Executando no VS Code

No terminal integrado (`Ctrl+`` `), dentro de `energy_data_project/`:

```bash
source .venv/bin/activate
export JAVA_HOME=/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home

lakehouse ingest --dataset indicadores_aneel
lakehouse silver
lakehouse gold
streamlit run app/dashboard.py   # opcional
```

Ou tudo de uma vez:

```bash
source .venv/bin/activate && \
export JAVA_HOME=/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home && \
lakehouse ingest --dataset indicadores_aneel && \
lakehouse silver && \
lakehouse gold
```

> Para não precisar exportar `JAVA_HOME` toda vez, adicione ao `~/.zshrc`:
> ```bash
> export JAVA_HOME=/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home
> ```

---

## Autor

Rafael Alvarenga
