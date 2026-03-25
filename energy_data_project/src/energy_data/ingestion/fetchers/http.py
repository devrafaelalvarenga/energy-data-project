from __future__ import annotations

import requests

from energy_data.core.exceptions import IngestionError


class HttpFetcher:
    """Responsável por baixar conteúdos via HTTP."""

    def fetch(self, source: str) -> bytes:
        """
        Baixa o conteúdo bruto de uma URL.

        Raises:
            IngestionError: quando o download falha.
        """
        try:
            response = requests.get(source, timeout=120)
            response.raise_for_status()
            return response.content
        except requests.RequestException as exc:
            raise IngestionError(f"Falha ao baixar conteúdo da fonte: {source}") from exc