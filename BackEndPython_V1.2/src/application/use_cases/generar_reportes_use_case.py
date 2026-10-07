from __future__ import annotations

import logging
from typing import Final

from src.application.dto.reporte_dto import ReporteRequestDTO
from src.domain.ports.outbound.reporte_generator import ReporteGenerator

logger: logging.Logger = logging.getLogger(__name__)

_REPORTE_HOJA_VIDA: Final[int] = 0
_REPORTE_INFO_LABORAL: Final[int] = 1
_REPORTE_PLANTILLA: Final[int] = 2
_REPORTE_TRIBUTARIA: Final[int] = 3
_REPORTE_MIGRADOS: Final[int] = 4
_REPORTE_DEFAULT: Final[int] = 5
_REPORTE_ESTADOS: Final[int] = 6


class GenerarReportesUseCase:
    def __init__(self, reporte_generator: ReporteGenerator) -> None:
        self._gen: ReporteGenerator = reporte_generator

    async def generar_async(self, dto: ReporteRequestDTO) -> bytes:
        logger.info(
            "reporte_solicitado",
            extra={"tipo": dto.tipo, "programa": dto.programa, "subprograma": dto.subprograma},
        )
        if dto.tipo == _REPORTE_HOJA_VIDA:
            return await self._gen.generar_hoja_vida_async(
                programa=dto.programa,
                subprograma=dto.subprograma,
                fecha_inicio=dto.fecha_inicio,
                fecha_fin=dto.fecha_fin,
            )
        if dto.tipo == _REPORTE_INFO_LABORAL:
            return await self._gen.generar_info_laboral_async(
                fecha_inicio=dto.fecha_inicio,
                fecha_fin=dto.fecha_fin,
            )
        if dto.tipo == _REPORTE_PLANTILLA:
            return await self._gen.generar_plantilla_participantes_async(
                programa=dto.programa,
                subprograma=dto.subprograma,
                fecha_inicio=dto.fecha_inicio,
                fecha_fin=dto.fecha_fin,
            )
        if dto.tipo == _REPORTE_TRIBUTARIA:
            return await self._gen.generar_info_tributaria_async(
                fecha_inicio=dto.fecha_inicio,
                fecha_fin=dto.fecha_fin,
            )
        if dto.tipo == _REPORTE_MIGRADOS:
            return await self._gen.generar_usuarios_migrados_async(
                fecha_inicio=dto.fecha_inicio,
                fecha_fin=dto.fecha_fin,
            )
        if dto.tipo == _REPORTE_ESTADOS:
            return await self._gen.generar_estados_perfiles_async(
                programa=dto.programa,
                subprograma=dto.subprograma,
                fecha_inicio=dto.fecha_inicio,
                fecha_fin=dto.fecha_fin,
                cedula=dto.cedula,
                estado=dto.estado,
            )
        return await self._gen.generar_default_async(
            programa=dto.programa,
            subprograma=dto.subprograma,
            fecha_inicio=dto.fecha_inicio,
            fecha_fin=dto.fecha_fin,
        )
