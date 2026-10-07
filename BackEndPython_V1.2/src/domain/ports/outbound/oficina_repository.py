from __future__ import annotations

from typing import Protocol

from src.domain.entities.oficina_entity import OficinaEntity


class OficinaRepository(Protocol):
    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        marca: str | None = None,
        regional: str | None = None,
        ind_activo: bool | None = None,
    ) -> tuple[list[OficinaEntity], int]: ...

    async def listar_activas_async(self) -> list[OficinaEntity]: ...

    async def obtener_por_id_async(self, cod_oficinas: int) -> OficinaEntity | None: ...

    async def crear_async(self, entity: OficinaEntity) -> OficinaEntity: ...

    async def actualizar_async(
        self, cod_oficinas: int, entity: OficinaEntity
    ) -> OficinaEntity | None: ...
