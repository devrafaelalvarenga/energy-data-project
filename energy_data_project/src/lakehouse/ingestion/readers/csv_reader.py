from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession

# Spark requer nomes canônicos de charset (IANA); mapeia aliases comuns
_ENCODING_ALIASES: dict[str, str] = {
    "latin-1": "iso-8859-1",
    "latin1": "iso-8859-1",
}


class SparkCsvReader:
    def __init__(self, spark: SparkSession) -> None:
        self.spark = spark

    def read(self, path: str, separator: str = ";", encoding: str = "latin-1") -> DataFrame:
        charset = _ENCODING_ALIASES.get(encoding.lower(), encoding)
        return (
            self.spark.read.option("header", "true")
            .option("sep", separator)
            .option("encoding", charset)
            .option("inferSchema", "true")
            .csv(path)
        )
