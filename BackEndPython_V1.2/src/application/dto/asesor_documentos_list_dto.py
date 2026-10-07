from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.asesor_documentos_item_dto import AsesorDocumentosItemDTO


@dataclass
class AsesorDocumentosListDTO:
    items: list[AsesorDocumentosItemDTO]
    total: int
    page: int
    page_size: int
