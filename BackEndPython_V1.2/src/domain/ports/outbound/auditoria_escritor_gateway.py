from __future__ import annotations

from typing import Protocol

from src.domain.entities.registro_auditoria import RegistroAuditoria


class AuditoriaEscritorGateway(Protocol):
    """AP-0028: puerto de escritura autonoma de un asiento de auditoria.

    La implementacion persiste el asiento en su propia transaccion, independiente de la
    operacion de negocio, para que el registro no dependa del exito o rollback de esta.
    """

    async def guardar_async(self, registro: RegistroAuditoria) -> None: ...
