from enum import Enum


class EstadoSesion(str, Enum):
    """AP-0130: ciclo de vida de una sesion en el registro central."""

    ACTIVA = "activa"
    REVOCADA = "revocada"
    EXPIRADA = "expirada"
