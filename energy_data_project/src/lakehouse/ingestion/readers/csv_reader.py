from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession


class SparkCsvReader:
    def __init__(self, spark: SparkSession) -> None:
        self.spark = spark

    def read(self, path: str, separator: str = ";", encoding: str = "latin-1") -> DataFrame:
        return (
            self.spark.read.option("header", "true")
            .option("sep", separator)
            .option("encoding", encoding)
            .option("inferSchema", "true")
            .csv(path)
        )
