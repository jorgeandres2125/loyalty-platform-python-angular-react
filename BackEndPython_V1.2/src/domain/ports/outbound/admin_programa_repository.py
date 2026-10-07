from __future__ import annotations

from typing import Protocol

from src.domain.entities.comisionista_programa_entity import (
    ComisionistaProgramaEntity,
)


class AdminProgramaRepository(Protocol):
    """Puerto outbound para edición administrativa de dbo.comisionistas_programa.

    Política decisión 3: solo lectura y actualización del `cp_nombre`. No expone
    `crear` ni `eliminar` porque los `cpid` están cableados en código y enums
    (1=Movilidad, 2=Consumo) y romperían el dominio si se eliminan.
    """

    async def listar_async(self) -> list[ComisionistaProgramaEntity]: ...
    async def obtener_por_id_async(
        self, cpid: int
    ) -> ComisionistaProgramaEntity | None: ...
    async def actualizar_nombre_async(
        self, cpid: int, nuevo_nombre: str
    ) -> ComisionistaProgramaEntity | None: ...
