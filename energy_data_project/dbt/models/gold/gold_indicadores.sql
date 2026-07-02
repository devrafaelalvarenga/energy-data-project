{{
  config(
    materialized='table',
    description='Modelo analítico Gold — DEC e FEC por distribuidora, conjunto e período.'
  )
}}

WITH base AS (
    SELECT
        sigla_agente,
        id_conjunto,
        nome_conjunto,
        CAST(ano AS INTEGER)     AS ano,
        CAST(periodo AS INTEGER) AS mes,
        UPPER(TRIM(sigla_indicador)) AS sigla_indicador,
        CAST(valor_indicador AS DOUBLE) AS valor_indicador
    FROM delta_scan('{{ env_var("SILVER_PATH", "../data/silver/aneel/indicadores_aneel") }}')
    WHERE UPPER(TRIM(sigla_indicador)) IN ('DEC', 'FEC')
),

pivoted AS (
    PIVOT base
    ON sigla_indicador IN ('DEC', 'FEC')
    USING first(valor_indicador)
    GROUP BY sigla_agente, id_conjunto, nome_conjunto, ano, mes
)

SELECT
    sigla_agente,
    id_conjunto,
    nome_conjunto,
    ano,
    mes,
    "DEC" AS dec,
    "FEC" AS fec,
    ano * 100 + mes                 AS ano_mes,
    make_date(ano, mes, 1)          AS data_referencia
FROM pivoted
