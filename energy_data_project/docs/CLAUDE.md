# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
> Este arquivo é o ponto de entrada da IA para este projeto.
> Ele funciona como um índice: não contém detalhes longos — aponta para os documentos certos.
> Toda instrução longa ou técnica vive em docs/. Este arquivo deve permanecer enxuto.

## 🗂️ Índice de Documentos Obrigatórios

> A IA deve ler todos os arquivos abaixo antes de executar qualquer tarefa.

|Arquivo |Descrição |Atualizado em|
|----------------------------|--------------------------------------------------------|-------------|
|`docs/arquitetura.md` |Stack, fluxo de dados e detalhamento de cada camada |02/07/2026 às 00h48 BRT|
|`docs/roadmap.md` |Tarefas pendentes, em andamento e concluídas |02/07/2026 às 00h48 BRT|
|`docs/changes.md` |Changelog de todas as alterações relevantes |02/07/2026 às 00h48 BRT|
|`docs/integracoes/README.md`|Índice de todas as integrações externas documentadas |— |

> Regra: toda vez que um arquivo acima for alterado, atualizar imediatamente o campo "Atualizado em" com a data e hora no fuso BRT (ex: `20/03/2025 às 14h32 BRT`).

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

- [ ] Toda alteração na estrutura de tabelas, funções, triggers ou fluxo de dados → atualizar docs/arquitetura.md
- [ ] Toda etapa concluída ou iniciada → atualizar docs/roadmap.md
- [ ] Toda mudança relevante → registrar em docs/changes.md com data e descrição
- [ ] Todo novo documento criado → referenciar no índice deste arquivo com a data
- [ ] Este arquivo (`CLAUDE.md`) deve permanecer enxuto — nunca adicionar conteúdo longo aqui

### Código

- [ ] Proibido cores hardcoded
- [ ] Tudo precisa ser documentado — funções, componentes, lógicas complexas e decisões de arquitetura
- [ ] Tudo precisa ser testado

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

-----

## Setup

Todos os comandos devem ser executados dentro de `energy_data_project/`.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Requer **Java 17+** instalado (necessário para PySpark):
```bash
brew install openjdk@17  # macOS
```

## Comandos do Pipeline

```bash
# Bronze — download ANEEL + escrita Delta Lake
lakehouse ingest --dataset indicadores_aneel

# Silver — limpeza, tipagem e validação (PySpark + Delta Lake)
lakehouse silver

# Gold — modelos analíticos (DBT + DuckDB lendo Delta)
lakehouse gold

# Dashboard — visualização interativa da camada Gold
streamlit run app/dashboard.py
```

## Testes, Lint, Types

```bash
pytest tests/unit/ -v --cov=src/lakehouse
pytest tests/unit/test_silver_transformations.py   # Silver específico
ruff check src/
mypy src/lakehouse/
```

## DBT (diretamente)

```bash
cd dbt
dbt run          # executa modelos Gold
dbt test         # valida qualidade da camada Gold
dbt run --select gold_indicadores  # modelo específico
```
