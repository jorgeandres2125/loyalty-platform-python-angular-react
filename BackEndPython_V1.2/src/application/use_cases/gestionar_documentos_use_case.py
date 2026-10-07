from __future__ import annotations

import logging

from src.application.dto.asesor_documentos_item_dto import AsesorDocumentosItemDTO
from src.application.dto.asesor_documentos_list_dto import AsesorDocumentosListDTO
from src.application.dto.documento_edit_dto import DocumentoEditDTO
from src.application.dto.documento_upload_dto import DocumentoUploadDTO
from src.application.dto.moderar_documento_dto import ModerarDocumentoDTO
from src.domain.entities.documento_entity import DocumentoEntity
from src.domain.ports.outbound.documento_repository import DocumentoRepository

logger: logging.Logger = logging.getLogger(__name__)


class GestionarDocumentosUseCase:
    def __init__(
        self,
        documento_repo: DocumentoRepository,
    ) -> None:
        self._documento_repo: DocumentoRepository = documento_repo

    async def subir_async(self, dto: DocumentoUploadDTO) -> DocumentoEntity:
        entity: DocumentoEntity = DocumentoEntity(
            numero_documento=dto.numero_documento,
            tipo=dto.tipo,
            nombre=dto.nombre,
        )
        saved: DocumentoEntity = await self._documento_repo.guardar_async(entity)
        logger.info(
            "documento_subido",
            extra={"numero_documento": dto.numero_documento, "tipo": dto.tipo},
        )
        return saved

    async def moderar_async(self, dto: ModerarDocumentoDTO) -> None:
        await self._documento_repo.actualizar_estado_async(dto.documento_id, dto.estado)
        logger.info(
            "documento_moderado",
            extra={
                "doc_id": dto.documento_id,
                "estado": dto.estado,
                "moderador": dto.uid_moderador,
            },
        )

    async def listar_por_asesor_async(self, numero_documento: str) -> list[DocumentoEntity]:
        return await self._documento_repo.listar_por_asesor_async(numero_documento)

    async def listar_asesores_con_documentos_async(
        self,
        programa: int,
        page: int,
        page_size: int,
        cedula: str | None = None,
        tipo_doc: str | None = None,
    ) -> AsesorDocumentosListDTO:
        rows, total = await self._documento_repo.listar_asesores_con_documentos_async(
            programa=programa, page=page, page_size=page_size, cedula=cedula, tipo_doc=tipo_doc,
        )
        items: list[AsesorDocumentosItemDTO] = [
            AsesorDocumentosItemDTO(
                tipo_documento=tipo_doc or "CC",
                numero_documento=num_doc,
                email=email,
            )
            for tipo_doc, num_doc, email in rows
        ]
        return AsesorDocumentosListDTO(items=items, total=total, page=page, page_size=page_size)

    async def editar_async(self, dto: DocumentoEditDTO) -> DocumentoEntity | None:
        if dto.estado is not None:
            estado_norm: str = dto.estado.strip().lower()
            if estado_norm not in {"pendiente", "revision", "aprobado"}:
                raise ValueError(f"Estado inválido: {dto.estado}")
        entity: DocumentoEntity | None = await self._documento_repo.actualizar_documento_async(
            did=dto.did, nombre=dto.nombre, estado=dto.estado, fecha=dto.fecha,
        )
        logger.info(
            "documento_editado",
            extra={"did": dto.did, "estado": dto.estado, "nombre": dto.nombre},
        )
        return entity

    async def eliminar_async(self, did: int) -> None:
        await self._documento_repo.eliminar_async(did)
        logger.info("documento_eliminado", extra={"did": did})
