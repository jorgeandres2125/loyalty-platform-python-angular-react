from __future__ import annotations

from typing import Protocol

from src.domain.entities.comisionista_subprograma_entity import ComisionistaSubprogramaEntity


class ComisionistaSubprogramaRepository(Protocol):
    """Puerto de salida — tabla comisionistas_subprograma."""

    async def listar_async(self, cpid: int | None = None) -> list[ComisionistaSubprogramaEntity]: ...
    async def obtener_async(self, cspid: int) -> ComisionistaSubprogramaEntity | None: ...
    async def guardar_async(self, entity: ComisionistaSubprogramaEntity) -> ComisionistaSubprogramaEntity: ...
