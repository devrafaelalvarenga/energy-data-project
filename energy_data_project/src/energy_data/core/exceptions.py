class ProjectError(Exception):
    """Exceção base do projeto."""


class ConfigurationError(ProjectError):
    """Erro de configuração do projeto."""


class IngestionError(ProjectError):
    """Erro durante a ingestão de dados."""


class ValidationError(ProjectError):
    """Erro de validação de dados."""