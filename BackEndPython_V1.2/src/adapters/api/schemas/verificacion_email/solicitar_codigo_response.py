from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SolicitarCodigoResponse(BaseModel):
    """Respuesta neutra (anti-enumeración): mismo mensaje exista o no el registro."""

    model_config = ConfigDict(extra="forbid")

    enviado: bool
    mensaje: str
    email_enmascarado: str | None = None
    expira_en_horas: int | None = None
