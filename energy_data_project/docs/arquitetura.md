# Arquitetura — Energy Data Project

## Visão Geral

Pipeline de engenharia de dados em arquitetura Medallion (Bronze → Silver → Gold) para processamento dos indicadores de continuidade do fornecimento de energia elétrica da ANEEL.

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
        │  Polars CSV parser
        ▼
┌───────────────┐
│ Camada BRONZE │  data/bronze/aneel/indicadores_aneel/dataset.parquet
│  (parquet     │  Schema original + colunas técnicas injetadas:
│   enriquecido)│  row_number, dataset, source, file_hash, ingestion_timestamp
└───────┬───────┘
        │  SilverProcessor
        ▼
┌───────────────┐
│ Camada SILVER │  data/silver/aneel/indicadores_aneel/dataset.parquet
│  (dados limpos│  Schema snake_case, tipos corretos, linhas inválidas removidas,
│  e validados) │  colunas derivadas: ano_mes, data_referencia
└───────┬───────┘
        │  GoldProcessor
        ▼
┌───────────────┐
│  Camada GOLD  │  data/gold/aneel/indicadores_gold.parquet
│  (modelo      │  Pivot DEC/FEC → colunas dec e fec por conjunto/período
│  analítico)   │
└───────┬───────┘
        │  Streamlit
        ▼
┌───────────────┐
│  Dashboard    │  app/dashboard.py
│  (visualização│  Série temporal, ranking por distribuidora, histograma
│  interativa)  │
└───────────────┘
```

---

## Detalhamento por Camada

### RAW
- Arquivo CSV original da ANEEL, salvo em bytes sem nenhuma transformação.
- Serve como ponto de reprocessamento e auditoria.
- Hash SHA-256 calculado neste ponto e propagado para as camadas seguintes.

### Bronze
Responsável: `IngestionOrchestrator` (`src/energy_data/ingestion/orchestrator.py`)

| Passo | Componente | O que faz |
|---|---|---|
| Download | `HttpFetcher` | GET na URL configurada em `configs/datasets.yml` |
| Escrita RAW | `LocalFileWriter` | Salva bytes brutos em `data/raw/` |
| Parsing | `CsvReader` | Lê CSV com separador `;` e encoding `latin-1` via Polars |
| Validação mínima | `validate_not_empty`, `validate_required_columns` | Garante que o DataFrame não chegou vazio |
| Enriquecimento | `_enrich()` | Adiciona `row_number`, `dataset`, `source`, `file_hash`, `ingestion_timestamp` |
| Escrita parquet | `ParquetWriter` | Salva em `data/bronze/` |
| Auditoria | `save_metadata()` | Persiste JSON em `data/audit/` com row_count, col_count, hash e paths |

### Silver
Responsável: `SilverProcessor` (`src/energy_data/silver/processor.py`)

Transformações aplicadas em sequência:

1. **`normalize_columns`** — renomeia colunas PascalCase do schema ANEEL para snake_case
   - ex.: `SigAgente` → `sigla_agente`, `VlrIndiceEnviado` → `valor_indicador`
2. **`clean_strings`** — strip + substitui string vazia por `null` nas colunas texto
3. **`cast_types`** — converte tipos:
   - `ano` → `Int32`, `periodo` → `Int8`
   - `valor_indicador`: trata vírgula decimal (`0,5` → `0.5`) e cast para `Float64`
   - `data_geracao` → `Date`
4. **`enrich`** — cria `ano_mes` (inteiro YYYYMM) e `data_referencia` (Date dia 1)
5. **`drop_invalid_rows`** — remove linhas com nulos em campos obrigatórios
6. **`validate_silver`** — levanta `ValidationError` se:
   - DataFrame vazio
   - Colunas obrigatórias ausentes
   - `sigla_agente` ou `sigla_indicador` nulos/vazios
   - `periodo` fora de 1–12
   - `valor_indicador` negativo

### Gold
Responsável: `GoldProcessor` (`src/energy_data/gold/processor.py`)

1. Filtra apenas registros com `sigla_indicador` em `["DEC", "FEC"]`
2. Pivot: cada linha do Silver vira uma coluna — `dec` e `fec` por `(sigla_agente, id_conjunto, nome_conjunto, ano, mes)`
3. Cria `ano_mes` e `data_referencia` no nível Gold
4. Escreve parquet em `data/gold/`

### Dashboard
Arquivo: `app/dashboard.py` — executado via `streamlit run app/dashboard.py`

- Lê o parquet Gold com `@st.cache_data`
- Filtros laterais: distribuidora, ano, conjunto
- Visualizações: série temporal (DEC ou FEC), ranking por distribuidora, histograma, tabela de preview

---

## Configuração

Toda a configuração de datasets fica em `configs/datasets.yml`:

```yaml
datasets:
  indicadores_aneel:
    url: <URL pública ANEEL>
    format: csv
    csv_options: { separator: ";", encoding: "latin-1" }
    raw_path: data/raw/aneel/indicadores_aneel
    bronze_path: data/bronze/aneel/indicadores_aneel
```

Para adicionar uma nova fonte: incluir entrada no YAML e implementar `Fetcher`/`Reader` conforme interfaces em `ingestion/fetchers/` e `ingestion/readers/`.

---

## Hierarquia de Exceções

```
ProjectError
├── ConfigurationError   # arquivo YAML ausente ou inválido
├── IngestionError       # falha no download ou escrita
└── ValidationError      # violação de qualidade de dados
```

Todas capturadas no ponto de entrada do CLI (`cli.py::main`) e exibidas ao usuário com exit code 1.
