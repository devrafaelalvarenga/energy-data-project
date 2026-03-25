from src.energy_data.core.config import load_config


def test_load_config() -> None:
    config = load_config("configs/datasets.yml")
    assert "indicadores_aneel" in config.datasets
