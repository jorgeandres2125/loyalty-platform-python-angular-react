from __future__ import annotations

from typing import Protocol


class SondaPrivilegioBd(Protocol):
    """AP-0056: puerto de sondeo de los roles privilegiados del principal de BD conectado.

    La implementacion consulta al motor que roles administrativos tiene el login actual, sin
    exponer detalles del proveedor. Devuelve la lista de roles privilegiados detectados.
    """

    async def roles_privilegiados(self) -> list[str]: ...
