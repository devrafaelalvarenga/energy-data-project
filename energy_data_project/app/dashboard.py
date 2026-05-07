from __future__ import annotations

from pathlib import Path

import polars as pl
import streamlit as st


GOLD_PATH = Path("data/gold/aneel/indicadores_gold.parquet")


@st.cache_data
def load_data(path: str) -> pl.DataFrame:
    """Carrega os dados da camada Gold."""
    return pl.read_parquet(path)


def ensure_required_columns(df: pl.DataFrame) -> None:
    """Valida colunas mínimas esperadas no dashboard."""
    required = ["sigla_agente", "ano", "mes"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")


def normalize_metric_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Padroniza nomes de métricas para minúsculo quando necessário."""
    rename_map: dict[str, str] = {}

    if "DEC" in df.columns and "dec" not in df.columns:
        rename_map["DEC"] = "dec"

    if "FEC" in df.columns and "fec" not in df.columns:
        rename_map["FEC"] = "fec"

    if "periodo" in df.columns and "mes" not in df.columns:
        rename_map["periodo"] = "mes"

    if "nome_agente" in df.columns and "nome_agente" not in df.columns:
        rename_map["nome_agente"] = "nome_agente"

    return df.rename(rename_map) if rename_map else df


def build_filters(df: pl.DataFrame) -> tuple[list[str], list[int], list[str]]:
    """Cria filtros laterais do dashboard."""
    agentes = sorted(df.get_column("sigla_agente").drop_nulls().unique().to_list())
    anos = sorted(df.get_column("ano").drop_nulls().unique().to_list())

    conjuntos: list[str] = []
    if "nome_conjunto" in df.columns:
        conjuntos = sorted(df.get_column("nome_conjunto").drop_nulls().unique().to_list())

    selected_agentes = st.sidebar.multiselect(
        "Distribuidoras",
        options=agentes,
        default=agentes[:5] if len(agentes) > 5 else agentes,
    )

    selected_anos = st.sidebar.multiselect(
        "Anos",
        options=anos,
        default=anos,
    )

    selected_conjuntos = st.sidebar.multiselect(
        "Conjuntos",
        options=conjuntos,
        default=[],
    )

    return selected_agentes, selected_anos, selected_conjuntos


def apply_filters(
    df: pl.DataFrame,
    agentes: list[str],
    anos: list[int],
    conjuntos: list[str],
) -> pl.DataFrame:
    """Aplica filtros ao DataFrame."""
    filtered = df

    if agentes:
        filtered = filtered.filter(pl.col("sigla_agente").is_in(agentes))

    if anos:
        filtered = filtered.filter(pl.col("ano").is_in(anos))

    if conjuntos and "nome_conjunto" in filtered.columns:
        filtered = filtered.filter(pl.col("nome_conjunto").is_in(conjuntos))

    return filtered


def build_time_series(df: pl.DataFrame, metric: str) -> pl.DataFrame:
    """Gera série temporal agregada por ano e mês."""
    if metric not in df.columns:
        return pl.DataFrame()

    result = (
        df.group_by(["ano", "mes"])
        .agg(pl.col(metric).mean().alias(metric))
        .sort(["ano", "mes"])
    )

    return result.with_columns(
        pl.concat_str(
            [
                pl.col("ano").cast(pl.Utf8),
                pl.lit("-"),
                pl.col("mes").cast(pl.Utf8).str.zfill(2),
            ]
        ).alias("periodo")
    )


def build_agent_ranking(df: pl.DataFrame, metric: str) -> pl.DataFrame:
    """Gera ranking médio por distribuidora."""
    if metric not in df.columns:
        return pl.DataFrame()

    return (
        df.group_by("sigla_agente")
        .agg(pl.col(metric).mean().alias(metric))
        .sort(metric, descending=True)
    )


def build_summary(df: pl.DataFrame) -> dict[str, float | int]:
    """Gera métricas resumidas para exibição."""
    summary: dict[str, float | int] = {
        "linhas": df.height,
        "distribuidoras": df.get_column("sigla_agente").n_unique() if "sigla_agente" in df.columns else 0,
    }

    if "dec" in df.columns:
        summary["dec_medio"] = round(df.get_column("dec").mean(), 2) if df.height else 0.0

    if "fec" in df.columns:
        summary["fec_medio"] = round(df.get_column("fec").mean(), 2) if df.height else 0.0

    return summary


def main() -> None:
    """Executa o dashboard Streamlit."""
    st.set_page_config(
        page_title="Qualidade do Fornecimento de Energia",
        layout="wide",
    )

    st.title("Dashboard de Qualidade do Fornecimento de Energia")
    st.caption("Camada Gold derivada de dados públicos da ANEEL")

    if not GOLD_PATH.exists():
        st.error(f"Arquivo Gold não encontrado: {GOLD_PATH}")
        st.stop()

    df = load_data(str(GOLD_PATH))
    df = normalize_metric_columns(df)
    ensure_required_columns(df)

    st.sidebar.header("Filtros")
    agentes, anos, conjuntos = build_filters(df)
    filtered = apply_filters(df, agentes, anos, conjuntos)

    if filtered.height == 0:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
        st.stop()

    summary = build_summary(filtered)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Linhas", f"{summary.get('linhas', 0):,}".replace(",", "."))
    col2.metric("Distribuidoras", int(summary.get("distribuidoras", 0)))
    col3.metric("DEC médio", summary.get("dec_medio", 0.0))
    col4.metric("FEC médio", summary.get("fec_medio", 0.0))

    st.subheader("Série temporal")
    chart_metric = st.radio(
        "Métrica",
        options=["dec", "fec"],
        horizontal=True,
    )

    ts = build_time_series(filtered, chart_metric)

    if ts.height > 0:
        st.line_chart(
            ts.to_pandas().set_index("periodo")[[chart_metric]]
        )
    else:
        st.info(f"A métrica '{chart_metric}' não está disponível na Gold.")

    st.subheader("Ranking por distribuidora")
    ranking_metric = st.selectbox(
        "Ranking por",
        options=["dec", "fec"],
        index=0,
    )

    ranking = build_agent_ranking(filtered, ranking_metric)

    if ranking.height > 0:
        st.bar_chart(
            ranking.to_pandas().set_index("sigla_agente")[[ranking_metric]]
        )
    else:
        st.info(f"A métrica '{ranking_metric}' não está disponível na Gold.")

    st.subheader("Base analítica")
    preview_cols = [col for col in ["sigla_agente", "nome_conjunto", "ano", "mes", "dec", "fec"] if col in filtered.columns]
    st.dataframe(filtered.select(preview_cols).to_pandas(), use_container_width=True)

    st.subheader("Distribuição dos indicadores")
    hist_metric = st.selectbox(
        "Histograma",
        options=[col for col in ["dec", "fec"] if col in filtered.columns],
        index=0,
    )
    st.bar_chart(
        filtered.select(hist_metric).to_pandas()
    )


if __name__ == "__main__":
    main()