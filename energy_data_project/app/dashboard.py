from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

GOLD_DB = Path("data/gold/lakehouse.duckdb")
GOLD_TABLE = "gold_indicadores"


@st.cache_data
def load_data(db_path: str, table: str) -> pd.DataFrame:
    conn = duckdb.connect(db_path, read_only=True)
    df = conn.execute(f"SELECT * FROM {table}").df()
    conn.close()
    return df


def build_filters(df: pd.DataFrame) -> tuple[list[str], list[int], list[str]]:
    agentes = sorted(df["sigla_agente"].dropna().unique().tolist())
    anos = sorted(df["ano"].dropna().unique().tolist())
    conjuntos: list[str] = []
    if "nome_conjunto" in df.columns:
        conjuntos = sorted(df["nome_conjunto"].dropna().unique().tolist())

    selected_agentes = st.sidebar.multiselect(
        "Distribuidoras", options=agentes, default=agentes[:5] if len(agentes) > 5 else agentes
    )
    selected_anos = st.sidebar.multiselect("Anos", options=anos, default=anos)
    selected_conjuntos = st.sidebar.multiselect("Conjuntos", options=conjuntos, default=[])

    return selected_agentes, selected_anos, selected_conjuntos


def apply_filters(
    df: pd.DataFrame,
    agentes: list[str],
    anos: list[int],
    conjuntos: list[str],
) -> pd.DataFrame:
    if agentes:
        df = df[df["sigla_agente"].isin(agentes)]
    if anos:
        df = df[df["ano"].isin(anos)]
    if conjuntos and "nome_conjunto" in df.columns:
        df = df[df["nome_conjunto"].isin(conjuntos)]
    return df


def build_time_series(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    if metric not in df.columns:
        return pd.DataFrame()
    ts = df.groupby(["ano", "mes"])[metric].mean().reset_index()
    ts = ts.sort_values(["ano", "mes"])
    ts["periodo"] = ts["ano"].astype(str) + "-" + ts["mes"].astype(str).str.zfill(2)
    return ts.set_index("periodo")[[metric]]


def build_agent_ranking(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    if metric not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby("sigla_agente")[metric]
        .mean()
        .reset_index()
        .sort_values(metric, ascending=False)
        .set_index("sigla_agente")
    )


def main() -> None:
    st.set_page_config(page_title="Modern Energy Lakehouse", layout="wide")
    st.title("Modern Energy Lakehouse")
    st.caption("Indicadores de continuidade ANEEL — Camada Gold (DBT + DuckDB)")

    if not GOLD_DB.exists():
        st.error(f"Base Gold não encontrada: {GOLD_DB}\nExecute `lakehouse gold` primeiro.")
        st.stop()

    df = load_data(str(GOLD_DB), GOLD_TABLE)

    if df.empty:
        st.warning("Tabela Gold está vazia.")
        st.stop()

    st.sidebar.header("Filtros")
    agentes, anos, conjuntos = build_filters(df)
    filtered = apply_filters(df, agentes, anos, conjuntos)

    if filtered.empty:
        st.warning("Nenhum dado com os filtros selecionados.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros", f"{len(filtered):,}".replace(",", "."))
    col2.metric("Distribuidoras", filtered["sigla_agente"].nunique())
    col3.metric("DEC médio", round(filtered["dec"].mean(), 2) if "dec" in filtered else "—")
    col4.metric("FEC médio", round(filtered["fec"].mean(), 2) if "fec" in filtered else "—")

    st.subheader("Série temporal")
    metric = st.radio("Métrica", ["dec", "fec"], horizontal=True)
    ts = build_time_series(filtered, metric)
    if not ts.empty:
        st.line_chart(ts)
    else:
        st.info(f"Métrica '{metric}' indisponível.")

    st.subheader("Ranking por distribuidora")
    ranking_metric = st.selectbox("Ranking por", ["dec", "fec"])
    ranking = build_agent_ranking(filtered, ranking_metric)
    if not ranking.empty:
        st.bar_chart(ranking)

    st.subheader("Base analítica")
    preview_cols = [c for c in ["sigla_agente", "nome_conjunto", "ano", "mes", "dec", "fec"] if c in filtered.columns]
    st.dataframe(filtered[preview_cols], use_container_width=True)


if __name__ == "__main__":
    main()
