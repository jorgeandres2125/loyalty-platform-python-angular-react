from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentoEditResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    did: int
    numero_documento: str
    tipo: int
    tipo_nombre: str
    nombre: str
    estado: str
    version: int
    fecha: datetime | None = None
