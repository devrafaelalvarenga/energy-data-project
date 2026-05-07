import polars as pl
import pytest
from energy_data.gold.validators import validate_gold


def test_gold_validation_fail_null():
    df = pl.DataFrame({
        "DEC": [None],
        "FEC": [5.0]
    })

    with pytest.raises(Exception):
        validate_gold(df)