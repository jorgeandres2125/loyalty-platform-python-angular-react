from __future__ import annotations

from pydantic import BaseModel


class ItemPoliticaRetencionResponse(BaseModel):
    """AP-0026: una entrada de la politica de retencion expuesta al auditor."""

    categoria: str
    dias: int
    base_regulatoria: str
