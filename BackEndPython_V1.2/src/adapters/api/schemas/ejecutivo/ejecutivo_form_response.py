from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class EjecutivoFormResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    tipo_documento: str
    numero_documento: str
    nombre_completo: str
    codigo_ejecutivo: str
    celular: str
    email: str
    perfil: str
    perfil_nombre: str
    estado: bool
