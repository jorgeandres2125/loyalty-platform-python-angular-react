from __future__ import annotations

from typing import Protocol

from src.domain.entities.comisionista_programa_entity import ComisionistaProgramaEntity


class ComisionistaProgramaRepository(Protocol):
    """Puerto de salida — tabla comisionistas_programa."""

    async def listar_async(self) -> list[ComisionistaProgramaEntity]: ...
    async def obtener_async(self, cpid: int) -> ComisionistaProgramaEntity | None: ...
    async def guardar_async(self, entity: ComisionistaProgramaEntity) -> ComisionistaProgramaEntity: ...
