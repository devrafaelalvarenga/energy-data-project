# Energy Data Project

Projeto de Engenharia de Dados para monitoramento da qualidade do fornecimento de energia elétrica no Brasil com dados públicos da ANEEL.

## Objetivo da Sprint 1
- Definir a arquitetura inicial
- Criar a estrutura real do projeto
- Implementar ingestão Bronze ponta a ponta
- Garantir rastreabilidade, logs e auditoria básica

## Como instalar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

## Como executar
energy-data ingest --dataset indicadores_aneel


---

## 18. Como executar

Depois de criar os arquivos:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
energy-data ingest --dataset indicadores_aneel

## resultado esperado

data/raw/aneel/indicadores_aneel/source_file.csv
data/bronze/aneel/indicadores_aneel/dataset.parquet
data/audit/indicadores_aneel_metadata.json