class LakehouseError(Exception):
    """Exceção base do projeto."""


class ConfigurationError(LakehouseError):
    """Erro de configuração."""


class IngestionError(LakehouseError):
    """Erro durante a ingestão de dados."""


class ValidationError(LakehouseError):
    """Erro de validação de dados."""
