from __future__ import annotations

import logging
from typing import Any

from src.application.dto.reporte_dto import ReporteRequestDTO
from src.application.dto.reporte_preview_response_dto import ReportePreviewResponseDTO
from src.domain.ports.outbound.reporte_generator import ReporteGenerator

logger: logging.Logger = logging.getLogger(__name__)


class ObtenerPreviewReportesUseCase:
    def __init__(self, reporte_generator: ReporteGenerator) -> None:
        self._gen: ReporteGenerator = reporte_generator

    async def obtener_async(self, dto: ReporteRequestDTO) -> ReportePreviewResponseDTO:
        logger.info(
            "reporte_preview_solicitado",
            extra={
                "tipo": dto.tipo,
                "programa": dto.programa,
                "subprograma": dto.subprograma,
                "page": dto.page,
                "page_size": dto.page_size,
            },
        )
        columns: list[str]
        rows: list[list[Any]]
        total: int
        columns, rows, total = await self._gen.obtener_preview_async(
            tipo=dto.tipo,
            programa=dto.programa,
            subprograma=dto.subprograma,
            fecha_inicio=dto.fecha_inicio,
            fecha_fin=dto.fecha_fin,
            cedula=dto.cedula,
            estado=dto.estado,
            page=dto.page,
            page_size=dto.page_size,
        )
        return ReportePreviewResponseDTO(
            columns=columns,
            rows=rows,
            total=total,
            page=dto.page,
            page_size=dto.page_size,
        )
