from __future__ import annotations

from typing import Protocol


class PasswordHistoryRepository(Protocol):
    """AP-0041: puerto de salida del historial de contrasenas por usuario (PEP 544).

    Guarda los hashes de las contrasenas usadas (nunca texto plano) para impedir su
    reutilizacion. Vive en la tabla lateral user_password_history; no toca dbo.users.
    """

    async def ultimos_hashes(self, uid: int, cantidad: int) -> list[str]: ...

    async def insertar(self, uid: int, password_hash: str, creado_iso: str) -> None: ...

    async def podar(self, uid: int, conservar: int) -> None: ...
