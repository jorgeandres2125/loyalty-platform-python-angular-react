from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FirmarRequest(BaseModel):
    """AP-0006: solicita la firma digital de un recurso o transaccion sensible."""

    model_config = ConfigDict(extra="forbid")

    recurso_tipo: str = Field(min_length=1, max_length=80)
    recurso_id: str = Field(min_length=1, max_length=120)
    payload: dict[str, object] = Field(
        description="Contenido a firmar; se canonicaliza y se firma su hash SHA-256.",
    )
