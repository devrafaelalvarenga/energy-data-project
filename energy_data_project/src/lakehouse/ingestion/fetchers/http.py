from __future__ import annotations

import requests

from lakehouse.core.exceptions import IngestionError
from lakehouse.core.logging import get_logger

logger = get_logger(__name__)


class HttpFetcher:
    def fetch(self, url: str, timeout: int = 120) -> bytes:
        logger.info("http.fetch.started", url=url)
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise IngestionError(f"Falha ao baixar {url}: {exc}") from exc
        logger.info("http.fetch.completed", url=url, bytes=len(response.content))
        return response.content
