from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AsesorDocumentosItemDTO:
    tipo_documento: str
    numero_documento: str
    email: str | None
