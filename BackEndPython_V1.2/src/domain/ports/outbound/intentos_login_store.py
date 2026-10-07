from __future__ import annotations

from typing import Protocol

from src.domain.value_objects.intentos_login import IntentosLogin


class IntentosLoginStore(Protocol):
    """Almacén con expiración (TTL) del conteo de fallos de login por clave (AP-0007).

    Contrato estructural (PEP 544): el adaptador por defecto es en memoria, pero un
    Redis/SQL puede sustituirlo sin cambiar la firma. El TTL lo aplica el adaptador y
    actúa como ventana de reinicio del contador.
    """

    async def obtener(self, clave: str) -> IntentosLogin | None: ...
    async def guardar(self, clave: str, registro: IntentosLogin) -> None: ...
    async def eliminar(self, clave: str) -> None: ...
