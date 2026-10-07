from __future__ import annotations

from typing import Protocol

from src.domain.entities.arl_entity import ArlEntity


class ArlRepository(Protocol):
    """Puerto outbound para el catálogo dbo.arl (Administradoras de Riesgos Laborales)."""

    async def listar_paginado_async(
        self, page: int, page_size: int, nombre: str | None = None
    ) -> tuple[list[ArlEntity], int]: ...

    async def obtener_por_id_async(self, tid: int) -> ArlEntity | None: ...

    async def crear_async(self, entity: ArlEntity) -> ArlEntity: ...

    async def actualizar_async(self, tid: int, entity: ArlEntity) -> ArlEntity | None: ...

    async def eliminar_async(self, tid: int) -> bool: ...

    async def existe_referenciado_async(self, tid: int) -> bool: ...
