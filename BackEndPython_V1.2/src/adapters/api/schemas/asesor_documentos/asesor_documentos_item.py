from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AsesorDocumentosItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo_documento: str
    numero_documento: str
    email: str | None = None
