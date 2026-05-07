# Energy Data Project

Pipeline de Engenharia de Dados desenvolvido para processamento e análise de indicadores de continuidade do fornecimento de energia elétrica disponibilizados pela ANEEL.

O projeto foi construído utilizando arquitetura em camadas (Bronze, Silver e Gold), seguindo boas práticas de engenharia de dados, com foco em organização, qualidade, rastreabilidade e análise de dados.

---

# Objetivo do Projeto

O objetivo deste projeto é construir um pipeline de dados completo capaz de:

- realizar ingestão de dados públicos da ANEEL;
- tratar e padronizar os dados;
- aplicar validações de qualidade;
- estruturar os dados em formato analítico;
- disponibilizar informações por meio de dashboard interativo.

---

# Fonte dos Dados

Dataset público da ANEEL:

https://dadosabertos.aneel.gov.br/dataset/d5f0712e-62f6-4736-8dff-9991f10758a7/resource/4493985c-baea-429c-9df5-3030422c71d7/download/indicadores-continuidade-coletivos-2020-2029.csv

---

# Arquitetura do Projeto

```text
Fonte CSV (ANEEL)
        ↓
Bronze Layer
(raw / ingestão)
        ↓
Silver Layer
(tratamento e validação)
        ↓
Gold Layer
(modelo analítico)
        ↓
Dashboard Streamlit
```

---

# Tecnologias Utilizadas

## Linguagem e Processamento

- Python 3.12+
- Polars
- PyArrow

## Visualização

- Streamlit

## Qualidade e Testes

- Pytest

## Versionamento

- Git
- GitHub

---

# Estrutura do Projeto

```text
energy_data_project/
├── app/
│   └── dashboard.py
├── configs/
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── src/
│   └── energy_data/
├── tests/
├── pyproject.toml
└── README.md
```

---

# Execução do Pipeline

## Ingestão Bronze

```bash
energy-data ingest --dataset indicadores_aneel
```

## Processamento Silver

```bash
energy-data silver
```

## Processamento Gold

```bash
energy-data gold
```

---

# Executando o Dashboard

## Instalar Streamlit

```bash
pip install streamlit
```

## Executar dashboard

```bash
streamlit run app/dashboard.py
```

---

# Funcionalidades do Dashboard

- análise temporal de DEC;
- análise temporal de FEC;
- comparação entre distribuidoras;
- filtros por ano;
- filtros por conjunto;
- ranking de indicadores;
- visualização tabular dos dados.

---

# Testes

## Executar todos os testes

```bash
pytest
```

---

# Melhorias Futuras

- orquestração com Apache Airflow;
- armazenamento em nuvem;
- integração com DuckDB;
- CI/CD automatizado;
- monitoramento de qualidade dos dados;
- arquitetura Lakehouse.

---

# Autor

Rafael Alvarenga
