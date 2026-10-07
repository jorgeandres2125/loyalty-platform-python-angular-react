from __future__ import annotations

from typing import Protocol

from src.domain.entities.comisionista_subprograma_entity import (
    ComisionistaSubprogramaEntity,
)


class AdminSubprogramaRepository(Protocol):
    """Puerto outbound para CRUD de dbo.comisionistas_subprograma."""

    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        cpid: int | None = None,
    ) -> tuple[list[ComisionistaSubprogramaEntity], int]: ...
    async def obtener_por_id_async(
        self, cspid: int
    ) -> ComisionistaSubprogramaEntity | None: ...
    async def crear_async(
        self, entity: ComisionistaSubprogramaEntity
    ) -> ComisionistaSubprogramaEntity: ...
    async def actualizar_async(
        self, cspid: int, entity: ComisionistaSubprogramaEntity
    ) -> ComisionistaSubprogramaEntity | None: ...
    async def eliminar_async(self, cspid: int) -> bool: ...
    async def existe_referenciado_async(self, cspid: int) -> bool: ...
