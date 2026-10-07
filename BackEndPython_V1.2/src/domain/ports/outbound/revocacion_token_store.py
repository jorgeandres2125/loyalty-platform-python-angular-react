from __future__ import annotations

from typing import Protocol


class RevocacionTokenStore(Protocol):
    """AP-0021: denylist de identificadores de token (jti) revocados.

    Contrato estructural (PEP 544). Revoca una sesion puntual (logout) hasta que el
    token expira naturalmente (TTL = vida restante), momento en que se purga. El
    adaptador por defecto es en memoria; en produccion un Redis o SQL (tabla
    revoked_token) sin cambiar la firma del puerto.
    """

    async def revocar(self, jti: str, ttl_segundos: int) -> None: ...
    async def esta_revocado(self, jti: str) -> bool: ...
