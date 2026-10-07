from __future__ import annotations

from fastapi import APIRouter, Depends

from src.adapters.api.schemas.retencion.item_politica_retencion_response import (
    ItemPoliticaRetencionResponse,
)
from src.adapters.api.schemas.retencion.politica_retencion_response import (
    PoliticaRetencionResponse,
)
from src.application.use_cases.obtener_politica_retencion_use_case import (
    ObtenerPoliticaRetencionUseCase,
)
from src.domain.value_objects.item_politica_retencion import ItemPoliticaRetencion
from src.infrastructure.config.dependencies import get_politica_retencion_uc, require_token

# AP-0026: politica de retencion de logs vigente. Requiere JWT; expone, como evidencia de
# auditoria, cuanto tiempo se conserva cada categoria de log y su base regulatoria.
router: APIRouter = APIRouter()


@router.get(
    "/politica-retencion",
    response_model=PoliticaRetencionResponse,
    summary="Consultar la politica de retencion de logs vigente (AP-0026)",
)
async def politica_retencion(
    token: dict[str, object] = Depends(require_token),
    uc: ObtenerPoliticaRetencionUseCase = Depends(get_politica_retencion_uc),
) -> PoliticaRetencionResponse:
    items: list[ItemPoliticaRetencion] = uc.ejecutar()
    return PoliticaRetencionResponse(
        items=[
            ItemPoliticaRetencionResponse(
                categoria=item.categoria.value,
                dias=item.dias,
                base_regulatoria=item.base_regulatoria,
            )
            for item in items
        ],
        total=len(items),
    )
