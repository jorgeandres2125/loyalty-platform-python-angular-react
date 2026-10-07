from __future__ import annotations

from typing import Protocol

from src.domain.entities.bloqueo_duro import BloqueoDuro


class BloqueoDuroRepository(Protocol):
    """AP-0157: persistencia del bloqueo duro de cuentas (por uid).

    Contrato estructural (PEP 544). El adaptador por defecto es en memoria (ambito de
    proceso); en produccion un adaptador SQL (tabla lateral user_account_lock) lo hace
    durable y compartido entre replicas sin cambiar la firma del puerto. Es independiente
    del estado de bloqueo suave (AP-0009, tabla user_lockout).
    """

    async def obtener(self, uid: int) -> BloqueoDuro | None: ...
    async def guardar(self, estado: BloqueoDuro) -> None: ...
    async def eliminar(self, uid: int) -> None: ...
