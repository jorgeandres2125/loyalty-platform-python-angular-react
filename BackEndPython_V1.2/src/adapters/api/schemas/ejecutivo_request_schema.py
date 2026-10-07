from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class EjecutivoRequest(BaseModel):
    usuario_asesor: str
    email_asesor: str = ""
    usuario_comisionista: str = ""
    email_comisionista: str = ""
    nombre_comisionista: str = ""
    fecha_registro: datetime | None = None
