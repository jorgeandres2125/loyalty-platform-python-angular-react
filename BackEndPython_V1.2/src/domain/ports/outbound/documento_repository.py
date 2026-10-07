from __future__ import annotations

from datetime import datetime
from typing import Protocol

from src.domain.entities.documento_entity import DocumentoEntity


class DocumentoRepository(Protocol):
    async def obtener_por_documento_tipo_async(self, numero_documento: str, tipo: int) -> DocumentoEntity | None: ...
    async def obtener_por_did_async(self, did: int) -> DocumentoEntity | None: ...
    async def guardar_async(self, entity: DocumentoEntity) -> DocumentoEntity: ...
    async def actualizar_estado_async(self, did: int, estado: str) -> None: ...
    async def actualizar_documento_async(
        self,
        did: int,
        nombre: str | None,
        estado: str | None,
        fecha: datetime | None,
    ) -> DocumentoEntity | None: ...
    async def listar_pendientes_async(self) -> list[DocumentoEntity]: ...
    async def listar_por_asesor_async(self, numero_documento: str) -> list[DocumentoEntity]: ...
    async def listar_asesores_con_documentos_async(
        self,
        programa: int,
        page: int,
        page_size: int,
        cedula: str | None = None,
        tipo_doc: str | None = None,
    ) -> tuple[list[tuple[str, str, str | None]], int]: ...
    async def eliminar_async(self, did: int) -> None: ...
