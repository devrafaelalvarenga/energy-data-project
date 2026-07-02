# Roadmap — Modern Energy Lakehouse

## Concluído

### Sprint 1 — Estrutura e Ingestão Bronze (2026-03-23 / 2026-03-24)
- [x] Estrutura do projeto com `pyproject.toml`, `src/` layout e CLI
- [x] Configuração de datasets via `configs/datasets.yml` com validação Pydantic
- [x] Ingestão Bronze: HttpFetcher, CsvReader (Polars), writers, orchestrator
- [x] Enriquecimento técnico Bronze: row_number, dataset, source, file_hash, ingestion_timestamp
- [x] Auditoria JSON em `data/audit/`
- [x] Hierarquia de exceções, logging estruturado (structlog)
- [x] Camada Silver com transformações e validações (Polars)
- [x] Testes unitários iniciais

### Sprint 3 — Gold, Dashboard e Testes (2026-05-07)
- [x] Camada Gold com pivot DEC/FEC (Polars)
- [x] Dashboard Streamlit com filtros, série temporal e rankings
- [x] CLI estendido com subcomandos silver e gold
- [x] Testes Gold

### Sprint 4 — Modern Energy Lakehouse (2026-07-02)
- [x] Migração para novo pacote `src/lakehouse/` (reescrita limpa, remove dead code)
- [x] Bronze reescrito com PySpark + Delta Lake
- [x] Silver reescrito com PySpark + Delta Lake (5 transformações com PySpark Column API)
- [x] Gold migrado para DBT + dbt-duckdb (lê Delta via `delta_scan`)
- [x] Dashboard atualizado para DuckDB (lê `data/gold/lakehouse.duckdb`)
- [x] GitHub Actions: `ci.yml` (lint + testes) e `pipeline.yml` (manual dispatch)
- [x] SparkSession factory com Delta Lake configurado (`core/spark.py`)
- [x] Testes unitários para transformações Bronze e Silver com PySpark local
- [x] DBT testes de qualidade: `not_null`, `accepted_values` no `schema.yml`
- [x] Remoção do pacote antigo `src/energy_data/` e todo dead code

---

## Próximos Passos

### Sprint 5 — Qualidade e Observabilidade
- [ ] Testes de integração end-to-end (ingest → silver → gold em local Spark)
- [ ] Cobertura de testes com relatório (`pytest --cov`)
- [ ] Testes DBT adicionais: singular tests para validar ausência de negativos em DEC/FEC
- [ ] Bronze schema contracts: validar colunas obrigatórias após ingestão

### Sprint 6 — Orquestração
- [ ] Orquestração do pipeline completo com Apache Airflow ou Prefect
- [ ] DAG: ingest → silver → gold encadeados
- [ ] Agendamento mensal alinhado com ciclo de publicação da ANEEL

### Sprint 7 — Armazenamento em Nuvem
- [ ] Upload dos Delta tables para Supabase Storage (S3-compatible)
- [ ] Integração com o `lakehouse-ingestor` para carga em PostgreSQL
- [ ] `profiles.yml` com perfil `prod` apontando para storage cloud

### Sprint 8 — Análise Avançada
- [ ] Novos modelos DBT: benchmarks regulatórios (limites DEC/FEC por classe)
- [ ] Modelo de série histórica com médias móveis
- [ ] Alertas para distribuidoras fora dos limites legais

### Sprint 9 — Lakehouse Production-Grade
- [ ] Delta Lake Optimize + Z-Order nas tabelas Silver (reduz scan de dados)
- [ ] Versionamento de schema com Delta Lake schema evolution
- [ ] Monitoramento de qualidade contínuo (Great Expectations ou dbt-expectations)
