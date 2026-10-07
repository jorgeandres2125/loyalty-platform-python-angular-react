from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class EjecutivoFormRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo_documento: Annotated[str, Field(min_length=1, max_length=10)]
    numero_documento: Annotated[str, Field(min_length=1, max_length=40)]
    nombre_completo: Annotated[str, Field(min_length=1, max_length=200)]
    codigo_ejecutivo: Annotated[str, Field(min_length=1, max_length=200)]
    email: Annotated[str, Field(min_length=3, max_length=254)]
    celular: Annotated[str, Field(default="", max_length=36)] = ""
    perfil: Annotated[str, Field(min_length=1, max_length=20)]
    estado: bool = True
