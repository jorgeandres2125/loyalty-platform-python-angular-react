from __future__ import annotations

from datetime import date
from typing import Final
from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from src.adapters.api.schemas.reporte.reporte_preview_request import ReportePreviewRequest
from src.adapters.api.schemas.reporte.reporte_preview_response import ReportePreviewResponse
from src.adapters.api.schemas.reporte.reporte_request import ReporteRequest
from src.application.dto.reporte_dto import ReporteRequestDTO
from src.application.dto.reporte_preview_response_dto import ReportePreviewResponseDTO
from src.application.use_cases.generar_reportes_use_case import GenerarReportesUseCase
from src.application.use_cases.obtener_preview_reportes_use_case import (
    ObtenerPreviewReportesUseCase,
)
from src.infrastructure.config.dependencies import get_preview_reportes_uc, get_reportes_uc
from src.shared.constants.content_types import CONTENT_TYPE_XLSX

router = APIRouter()

_FILENAME_PREFIX: Final[dict[int, str]] = {
    0: "hoja_vida",
    1: "info_laboral",
    2: "plantilla_participantes",
    3: "info_tributaria",
    4: "usuarios_migrados",
    5: "listado",
    6: "estados_perfiles",
}


@router.post("/generar", summary="Generar reporte Excel (7 tipos legacy)")
async def generar_reporte(
    body: ReporteRequest,
    uc: GenerarReportesUseCase = Depends(get_reportes_uc),
) -> Response:
    dto: ReporteRequestDTO = ReporteRequestDTO(
        tipo=body.tipo,
        programa=body.programa,
        subprograma=body.subprograma,
        fecha_inicio=body.fecha_inicio,
        fecha_fin=body.fecha_fin,
        cedula=body.cedula,
        estado=body.estado,
    )
    data: bytes = await uc.generar_async(dto)
    prefix: str = _FILENAME_PREFIX.get(body.tipo, "reporte")
    sufijo_programa: str = (
        ""
        if body.tipo in (1, 3, 4)
        else ("_movilidad" if body.programa == 1 else "_consumo")
    )
    filename: str = f"{prefix}{sufijo_programa}_{date.today().isoformat()}.xlsx"
    return Response(
        content=data,
        media_type=CONTENT_TYPE_XLSX,
        headers={"Content-Disposition": f"attachment; filename={quote(filename)}"},
    )


@router.post(
    "/preview",
    summary="Vista previa paginada de un reporte",
    response_model=ReportePreviewResponse,
)
async def obtener_preview_reporte(
    body: ReportePreviewRequest,
    uc: ObtenerPreviewReportesUseCase = Depends(get_preview_reportes_uc),
) -> ReportePreviewResponse:
    dto: ReporteRequestDTO = ReporteRequestDTO(
        tipo=body.tipo,
        programa=body.programa,
        subprograma=body.subprograma,
        fecha_inicio=body.fecha_inicio,
        fecha_fin=body.fecha_fin,
        cedula=body.cedula,
        estado=body.estado,
        page=body.page,
        page_size=body.page_size,
    )
    result: ReportePreviewResponseDTO = await uc.obtener_async(dto)
    return ReportePreviewResponse(
        columns=result.columns,
        rows=result.rows,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )
