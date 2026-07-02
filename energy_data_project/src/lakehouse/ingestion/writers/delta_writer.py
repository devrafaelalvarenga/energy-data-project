from __future__ import annotations

from pyspark.sql import DataFrame

from lakehouse.core.logging import get_logger

logger = get_logger(__name__)


class DeltaWriter:
    def write(self, df: DataFrame, path: str, mode: str = "overwrite") -> None:
        logger.info("delta.write.started", path=path, mode=mode)
        (
            df.write.format("delta")
            .mode(mode)
            .option("overwriteSchema", "true")
            .save(path)
        )
        logger.info("delta.write.completed", path=path, rows=df.count())
