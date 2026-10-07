from enum import StrEnum


class ResourceType(StrEnum):
    """AP-0055: tipos de objeto sensible sujetos a autorizacion a nivel de recurso."""

    DOCUMENTO = "documento"
    TOKEN_SAPIN = "token_sapin"
    DESAFIO_OOB = "desafio_oob"
    EVIDENCIA_FIRMA = "evidencia_firma"
