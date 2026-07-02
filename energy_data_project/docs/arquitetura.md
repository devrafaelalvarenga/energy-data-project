# Arquitetura — Modern Energy Lakehouse

## Visão Geral

Pipeline de engenharia de dados em arquitetura Medallion (Bronze → Silver → Gold) com stack enterprise: PySpark para processamento, Delta Lake como formato de armazenamento, DBT+DuckDB para a camada analítica e Streamlit para visualização.

```
Fonte pública (ANEEL)
        │
        │  HTTP GET (CSV ; latin-1)
        ▼
┌───────────────┐
│   Camada RAW  │  data/raw/aneel/indicadores_aneel/source_file.csv
│  (bytes brutos│  Arquivo preservado sem modificações
│    on disk)   │
└───────┬───────┘
        │  PySpark (SparkCsvReader)
        ▼
┌───────────────┐
│ Camada BRONZE │  data/bronze/aneel/indicadores_aneel/  (Delta Lake)
│  (Delta Lake) │  Schema original + metadados técnicos:
│               │  row_number, dataset, source, file_hash, ingestion_timestamp
└───────┬───────┘
        │  PySpark + Delta Lake (SilverProcessor)
        ▼
┌───────────────┐
│ Camada SILVER │  data/silver/aneel/indicadores_aneel/  (Delta Lake)
│  (Delta Lake  │  Schema snake_case, tipos corretos, linhas inválidas removidas,
│   + schema    │  colunas derivadas: ano_mes, data_referencia
│  enforcement) │
└───────┬───────┘
        │  DBT + DuckDB (delta extension)
        ▼
┌───────────────┐
│  Camada GOLD  │  data/gold/lakehouse.duckdb  (DuckDB database)
│  (DuckDB +    │  Tabela: gold_indicadores
│    DBT)       │  Pivot DEC/FEC → colunas dec e fec por conjunto/período
└───────┬───────┘
        │  duckdb.connect (read_only)
        ▼
┌───────────────┐
│  Dashboard    │  app/dashboard.py  (Streamlit)
│  (Streamlit + │  Série temporal, ranking, histograma, filtros interativos
│   DuckDB)     │
└───────────────┘
```

---

## Stack de Tecnologias

| Camada | Tecnologia | Papel |
|---|---|---|
| Ingestão HTTP | Python requests | Download do CSV público da ANEEL |
| Bronze | PySpark + Delta Lake | Parsing CSV, enriquecimento técnico, escrita Delta |
| Silver | PySpark + Delta Lake | Transformações, limpeza, validações, escrita Delta |
| Gold | DBT + dbt-duckdb | Modelos SQL analíticos via DuckDB sobre Delta |
| Armazenamento | Delta Lake (Parquet + transaction log) | Formato único para Bronze e Silver |
| Query Engine | DuckDB (delta extension) | Lê Delta Lake diretamente, executa SQL dos modelos DBT |
| Output Gold | DuckDB (.duckdb file) | Banco de dados que persiste tabelas Gold |
| Dashboard | Streamlit + duckdb | Visualização interativa da camada Gold |
| CI/CD | GitHub Actions | Lint + testes em push; pipeline completo via dispatch |

---

## Detalhamento por Camada

### RAW
- CSV original da ANEEL salvo em bytes sem modificação em `data/raw/`
- Hash SHA-256 calculado aqui e propagado para Bronze

### Bronze
Responsável: `BronzeProcessor` → `IngestionOrchestrator`

| Passo | Componente | O que faz |
|---|---|---|
| Download | `HttpFetcher` | GET na URL de `configs/datasets.yml`, timeout 120s |
| Escrita RAW | `LocalFileWriter` | Salva bytes brutos em `data/raw/` |
| Parsing | `SparkCsvReader` | `spark.read.csv` com sep=`;`, encoding=`latin-1` |
| Enriquecimento | `IngestionOrchestrator._enrich` | Adiciona `row_number` (monotonically_increasing_id), `dataset`, `source`, `file_hash`, `ingestion_timestamp` |
| Escrita Delta | `DeltaWriter` | `df.write.format("delta").mode("overwrite").save(bronze_path)` |
| Auditoria | `save_metadata()` | JSON em `data/audit/` com row_count, col_count, hash e paths |

### Silver
Responsável: `SilverProcessor`

Transformações PySpark em sequência:

1. **`normalize_columns`** — renomeia colunas PascalCase ANEEL → snake_case via `withColumnRenamed`
2. **`clean_strings`** — `trim()` + substitui string vazia por `null` via `when(..., None).otherwise(...)`
3. **`cast_types`** — `ano` → IntegerType, `periodo` → ByteType, `valor_indicador` → trata vírgula decimal com `regexp_replace` + cast DoubleType, `data_geracao` → DateType
4. **`enrich`** — cria `ano_mes` (Int YYYYMM) e `data_referencia` (Date dia 1 via `to_date` + `concat`)
5. **`drop_invalid_rows`** — `dropna(subset=[sigla_agente, sigla_indicador, ano, periodo, valor_indicador])`
6. **`_validate`** — levanta `ValidationError` se DataFrame vazio, colunas faltando, `periodo` fora de 1–12 ou `valor_indicador` negativo

Escrita: `df.write.format("delta").mode("overwrite").option("overwriteSchema","true").save(silver_path)`

### Gold (DBT)
Responsável: `dbt/models/gold/gold_indicadores.sql`

1. `delta_scan(silver_path)` — DuckDB lê Delta Lake diretamente via extensão `delta`
2. Filtra `sigla_indicador IN ('DEC', 'FEC')`
3. `PIVOT ON sigla_indicador` — gera colunas `dec` e `fec` por `(sigla_agente, id_conjunto, nome_conjunto, ano, mes)`
4. Cria `ano_mes` e `data_referencia`
5. Materializado como `TABLE` no DuckDB database em `data/gold/lakehouse.duckdb`

**Testes DBT** (`schema.yml`): `not_null` em todos os campos chave; `accepted_values` para `mes` (1–12).

### Dashboard
Arquivo: `app/dashboard.py`

- `duckdb.connect("data/gold/lakehouse.duckdb", read_only=True)` — sem concorrência com dbt
- Query: `SELECT * FROM gold_indicadores` → pandas DataFrame
- Resultado cacheado com `@st.cache_data`
- Filtros: distribuidora, ano, conjunto
- Painis: KPIs, série temporal, ranking, tabela, histograma

---

## Configuração

`configs/datasets.yml` — fonte única de verdade para URL, opções CSV e paths:

```yaml
datasets:
  indicadores_aneel:
    url: <URL pública ANEEL>
    csv_options: { separator: ";", encoding: "latin-1" }
    raw_path: data/raw/aneel/indicadores_aneel
    bronze_path: data/bronze/aneel/indicadores_aneel
```

Silver path é derivado automaticamente substituindo `bronze` por `silver` na config.

---

## SparkSession

Criada via `core/spark.py::get_spark()` em modo local:

```python
SparkSession.builder
  .master("local[*]")
  .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.2.0")
  .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
  .config("spark.sql.catalog.spark_catalog", "...DeltaCatalog")
```

---

## CI/CD (GitHub Actions)

| Workflow | Trigger | Passos |
|---|---|---|
| `ci.yml` | push/PR → main | Setup Java 17 + Python 3.11 → ruff → mypy → pytest tests/unit/ |
| `pipeline.yml` | workflow_dispatch (manual) | ingest → silver → dbt run → dbt test |

---

## Hierarquia de Exceções

```
LakehouseError
├── ConfigurationError   # YAML ausente ou inválido
├── IngestionError       # falha no download ou escrita
└── ValidationError      # violação de qualidade de dados
```
