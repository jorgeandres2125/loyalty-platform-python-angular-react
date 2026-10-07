from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class VerificarFirmaRequest(BaseModel):
    """AP-0006: verifica una firma digital sobre un payload."""

    model_config = ConfigDict(extra="forbid")

    payload: dict[str, object]
    valor_firma: str = Field(min_length=1, max_length=2048)
