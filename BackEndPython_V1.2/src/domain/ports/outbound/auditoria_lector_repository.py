from __future__ import annotations

from typing import Protocol

from src.domain.entities.registro_auditoria import RegistroAuditoria
from src.domain.value_objects.filtro_auditoria import FiltroAuditoria


class AuditoriaLectorRepository(Protocol):
    """AP-0028: puerto de lectura del historial de auditoria de un usuario.

    Solo expone consulta por usuario (el endpoint siempre filtra por el usuario del token),
    con paginacion y filtros. Nunca ofrece una lectura global sin usuario.
    """

    async def listar_por_usuario_async(
        self, user_id: int, filtro: FiltroAuditoria
    ) -> list[RegistroAuditoria]: ...

    async def contar_por_usuario_async(
        self, user_id: int, filtro: FiltroAuditoria
    ) -> int: ...
