from __future__ import annotations

import logging

from src.application.dto.ejecutivo_dto import EjecutivoDTO
from src.domain.entities.ejecutivo_catalogo_entity import EjecutivoCatalogoEntity
from src.domain.ports.outbound.referencia_repository import ReferenciaRepository

logger: logging.Logger = logging.getLogger(__name__)


class GestionarReferenciasUseCase:
    def __init__(self, referencia_repo: ReferenciaRepository) -> None:
        self._referencia_repo: ReferenciaRepository = referencia_repo

    async def listar_ejecutivos_async(self) -> list[EjecutivoCatalogoEntity]:
        return await self._referencia_repo.listar_ejecutivos_async()

    async def crear_ejecutivo_async(self, dto: EjecutivoDTO) -> EjecutivoCatalogoEntity:
        entity: EjecutivoCatalogoEntity = EjecutivoCatalogoEntity(
            usuario_asesor=dto.usuario_asesor,
            email_asesor=dto.email_asesor,
            usuario_comisionista=dto.usuario_comisionista,
            email_comisionista=dto.email_comisionista,
            nombre_comisionista=dto.nombre_comisionista,
            fecha_registro=dto.fecha_registro,
        )
        saved: EjecutivoCatalogoEntity = await self._referencia_repo.guardar_ejecutivo_async(entity)
        logger.info("ejecutivo_creado", extra={"usuario_asesor": dto.usuario_asesor})
        return saved
