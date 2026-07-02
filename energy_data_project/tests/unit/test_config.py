from lakehouse.core.config import load_config


def test_load_config() -> None:
    config = load_config("configs/datasets.yml")
    assert "indicadores_aneel" in config.datasets


def test_dataset_fields() -> None:
    config = load_config("configs/datasets.yml")
    ds = config.datasets["indicadores_aneel"]
    assert ds.csv_options.separator == ";"
    assert ds.csv_options.encoding == "latin-1"
    assert ds.bronze_path != ""
