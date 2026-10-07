from __future__ import annotations

from typing import Protocol


class EstadoCredencialRepository(Protocol):
    """AP-0021: version de credencial (token_version) por usuario.

    Contrato estructural (PEP 544). El token_version se embebe en el JWT (claim tv) y
    se compara en cada peticion; incrementarlo invalida de golpe todas las sesiones del
    usuario (cambio de contrasena, cierre de sesion global, deshabilitacion). El
    adaptador por defecto es en memoria; en produccion un adaptador SQL (tabla
    user_token_version) lo hace durable sin cambiar la firma.
    """

    async def obtener_version(self, uid: int) -> int: ...
    async def incrementar_version(self, uid: int) -> int: ...
