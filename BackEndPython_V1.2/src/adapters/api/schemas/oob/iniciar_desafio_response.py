from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class IniciarDesafioResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requiere_oob: bool
    enviado: bool
    desafio_id: str | None = None
    estado: str | None = None
    canal: str | None = None
    email_enmascarado: str | None = None
    expira_en_segundos: int | None = None
    mensaje: str
