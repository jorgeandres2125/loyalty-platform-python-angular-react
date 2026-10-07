from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.asesor_documentos.asesor_documentos_item import (
    AsesorDocumentosItem,
)


class AsesorDocumentosListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AsesorDocumentosItem]
    total: int
    page: int
    page_size: int
