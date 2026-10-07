from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ResolverDesafioRequest(BaseModel):
    """AP-0005: aprueba (con codigo) o rechaza un desafio OOB."""

    model_config = ConfigDict(extra="forbid")

    aprobar: bool
    codigo: str | None = Field(
        default=None, pattern=r"^\d{6}$", description="6 digitos si se aprueba"
    )
