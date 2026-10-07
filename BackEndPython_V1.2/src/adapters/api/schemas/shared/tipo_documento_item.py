from __future__ import annotations

from pydantic import BaseModel


class TipoDocumentoItem(BaseModel):
    codigo: str
    nombre: str
