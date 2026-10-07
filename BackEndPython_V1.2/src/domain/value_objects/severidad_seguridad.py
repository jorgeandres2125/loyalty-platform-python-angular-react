from enum import Enum


class SeveridadSeguridad(str, Enum):
    """Severidad de un evento excepcional o de seguridad (AP-0023).

    Escala ordenada (informativa < baja < media < alta < critica). Es una
    clasificación de seguridad propia, distinta del nivel de logging: cada evento
    de auditoría lleva su `severidad` además del `level` del logger. El adaptador de
    logging mapea cada severidad a un nivel estándar (INFO/WARNING/ERROR/CRITICAL).
    """

    INFORMATIVA = "informativa"
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"
