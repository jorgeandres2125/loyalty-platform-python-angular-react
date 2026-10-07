from __future__ import annotations

from typing import Protocol

from src.domain.entities.ejecutivo_entity import EjecutivoEntity


class EjecutivoRepository(Protocol):
    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        tipo_doc: str | None = None,
        documento: str | None = None,
        perfil: str | None = None,
        estado: bool | None = None,
    ) -> tuple[list[EjecutivoEntity], int]: ...

    async def obtener_por_id_async(self, ejecutivo_id: int) -> EjecutivoEntity | None: ...

    async def obtener_por_numero_documento_async(
        self, numero_documento: str
    ) -> EjecutivoEntity | None: ...

    async def crear_async(self, entity: EjecutivoEntity) -> EjecutivoEntity: ...

    async def actualizar_async(
        self, ejecutivo_id: int, entity: EjecutivoEntity
    ) -> EjecutivoEntity | None: ...
