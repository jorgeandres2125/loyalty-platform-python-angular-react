from __future__ import annotations

from typing import Protocol

from src.domain.entities.afp_entity import AfpEntity


class AfpRepository(Protocol):
    """Puerto outbound para el catálogo dbo.afp (Fondos de pensiones).

    Convención: las operaciones de mutación devuelven la entidad afectada.
    `existe_referenciado_async` permite al UC bloquear deletes con FK colgantes
    (política 1C de Panel de Control — hard delete con guardia de integridad).
    """

    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
    ) -> tuple[list[AfpEntity], int]: ...

    async def listar_todos_async(self) -> list[AfpEntity]: ...

    async def obtener_por_id_async(self, tid: int) -> AfpEntity | None: ...

    async def crear_async(self, entity: AfpEntity) -> AfpEntity: ...

    async def actualizar_async(
        self, tid: int, entity: AfpEntity
    ) -> AfpEntity | None: ...

    async def eliminar_async(self, tid: int) -> bool: ...

    async def existe_referenciado_async(self, tid: int) -> bool: ...
