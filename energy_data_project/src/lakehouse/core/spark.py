from __future__ import annotations

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession


def get_spark(app_name: str = "modern-energy-lakehouse") -> SparkSession:
    """Cria ou reutiliza uma SparkSession com suporte a Delta Lake."""
    builder = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.showConsoleProgress", "false")
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()
