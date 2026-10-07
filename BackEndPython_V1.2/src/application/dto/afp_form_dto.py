from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AfpFormDTO:
    """DTO de entrada para crear / actualizar una AFP del catálogo dbo.afp."""
    nombre: str
    nit: str | None = None
