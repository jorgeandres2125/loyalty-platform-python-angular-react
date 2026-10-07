from __future__ import annotations

from typing import Protocol

from src.domain.entities.canal_entity import CanalEntity


class CanalRepository(Protocol):
    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        ind_activo: bool | None = None,
    ) -> tuple[list[CanalEntity], int]: ...

    async def listar_activas_async(self) -> list[CanalEntity]: ...

    async def obtener_por_id_async(self, cod_canales: int) -> CanalEntity | None: ...

    async def crear_async(self, entity: CanalEntity) -> CanalEntity: ...

    async def actualizar_async(
        self, cod_canales: int, entity: CanalEntity
    ) -> CanalEntity | None: ...
