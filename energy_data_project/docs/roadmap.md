# Roadmap — Energy Data Project

## Concluído

### Sprint 1 — Estrutura e Ingestão Bronze (2026-03-23 / 2026-03-24)
- [x] Estrutura do projeto com `pyproject.toml`, `src/` layout e entry point `energy-data` CLI
- [x] Configuração de datasets via `configs/datasets.yml` com validação Pydantic
- [x] Camada de ingestão Bronze completa:
  - `HttpFetcher` para download da fonte pública ANEEL
  - `CsvReader` com suporte a encoding `latin-1` e separador `;`
  - `LocalFileWriter` para persistência dos bytes RAW
  - `ParquetWriter` para escrita Bronze
  - `IngestionOrchestrator` compondo todos os componentes
- [x] Enriquecimento técnico do Bronze: `row_number`, `dataset`, `source`, `file_hash`, `ingestion_timestamp`
- [x] Auditoria em JSON (`data/audit/`) com metadados da ingestão
- [x] Hierarquia de exceções: `ProjectError`, `ConfigurationError`, `IngestionError`, `ValidationError`
- [x] Logging estruturado com `structlog`
- [x] Camada Silver com transformações, validações e writer
- [x] Testes unitários iniciais (`tests/unit/test_config.py`)
- [x] `bootstrap_project.py` para scaffolding inicial

### Sprint 3 — Gold, Dashboard e Testes (2026-05-07)
- [x] Camada Gold (`GoldProcessor`): pivot DEC/FEC, modelo analítico por conjunto/período
- [x] Validadores da camada Gold (`gold/validators.py`)
- [x] CLI estendido com subcomandos `silver` e `gold`
- [x] Dashboard Streamlit (`app/dashboard.py`):
  - Série temporal de DEC e FEC
  - Ranking por distribuidora
  - Histograma de indicadores
  - Filtros por distribuidora, ano e conjunto
  - Tabela de preview da base analítica
- [x] Testes Gold: `test_gold_processor.py`, `test_gold_validators.py`
- [x] README expandido com instruções completas de uso

---

## Próximos Passos

### Sprint 4 — Qualidade e Observabilidade
- [ ] Completar testes em `tests/data_quality/` e `tests/integration/`
- [ ] Testes para a camada Silver (transformações e validações)
- [ ] Cobertura de testes com relatório (`pytest --cov`)
- [ ] Validação de schema Bronze com contratos em `bronze/contracts.py`

### Sprint 5 — Orquestração
- [ ] Orquestração do pipeline completo com Apache Airflow ou Prefect
- [ ] DAG: ingest → silver → gold encadeados automaticamente
- [ ] Agendamento diário/mensal conforme atualização da fonte ANEEL

### Sprint 6 — Armazenamento em Nuvem
- [ ] Upload dos parquets para Supabase Storage (bucket compatível com S3)
- [ ] Integração com o `lakehouse-ingestor` para carga no PostgreSQL
- [ ] Migração do storage local para cloud-native

### Sprint 7 — Análise Avançada
- [ ] Integração com DuckDB para queries ad-hoc sobre os parquets
- [ ] Cálculo de benchmarks regulatórios (limites DEC/FEC por classe de distribuidora)
- [ ] Alertas automáticos para distribuidoras fora dos limites

### Sprint 8 — CI/CD e Monitoramento
- [ ] Pipeline CI com GitHub Actions: lint (ruff), type check (mypy), testes
- [ ] Monitoramento de qualidade dos dados com Great Expectations ou Pandera
- [ ] Versionamento de schema dos parquets (Delta Lake ou Iceberg)
