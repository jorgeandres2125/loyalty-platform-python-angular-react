from __future__ import annotations

from typing import Protocol

from src.domain.entities.bloqueo_cuenta import BloqueoCuenta


class BloqueoCuentaRepository(Protocol):
    """AP-0009: persistencia del estado de bloqueo de cuentas.

    Contrato estructural (PEP 544). El adaptador por defecto es en memoria (ambito de
    proceso); en produccion un adaptador SQL (tabla user_lockout) lo hace durable y
    compartido entre replicas sin cambiar la firma del puerto.
    """

    async def obtener(self, clave: str) -> BloqueoCuenta | None: ...
    async def guardar(self, estado: BloqueoCuenta) -> None: ...
    async def eliminar(self, clave: str) -> None: ...
