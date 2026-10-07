from enum import StrEnum


class AccionRecurso(StrEnum):
    """AP-0055: accion solicitada sobre un objeto sensible (granularidad por accion)."""

    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    DOWNLOAD = "download"
    APPROVE = "approve"
    RESOLVE = "resolve"
