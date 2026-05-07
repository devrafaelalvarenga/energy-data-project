import polars as pl
from energy_data.gold.processor import GoldProcessor


def test_gold_transformation_basic():
    # Dados simulados (mock)
    df = pl.DataFrame({
        "sigla_agente": ["A", "A"],
        "nome_agente": ["Agente A", "Agente A"],
        "id_conjunto": [1, 1],
        "nome_conjunto": ["C1", "C1"],
        "ano": [2024, 2024],
        "mes": [1, 1],
        "sigla_indicador": ["DEC", "FEC"],
        "valor_indicador": [10.5, 5.2]
    })

    processor = GoldProcessor()
    df_gold = processor._transform(df)

    assert "DEC" in df_gold.columns
    assert "FEC" in df_gold.columns
    assert df_gold.height == 1