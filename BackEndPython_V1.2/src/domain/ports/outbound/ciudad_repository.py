from __future__ import annotations

from typing import Protocol

from src.domain.entities.ciudad_entity import CiudadEntity


class CiudadRepository(Protocol):
    """Puerto outbound para dbo.ciudades."""

    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        did: int | None = None,
    ) -> tuple[list[CiudadEntity], int]: ...
    async def obtener_por_id_async(self, cid: int) -> CiudadEntity | None: ...
    async def crear_async(self, entity: CiudadEntity) -> CiudadEntity: ...
    async def actualizar_async(self, cid: int, entity: CiudadEntity) -> CiudadEntity | None: ...
    async def eliminar_async(self, cid: int) -> bool: ...
    async def existe_referenciado_async(self, cid: int) -> bool: ...
