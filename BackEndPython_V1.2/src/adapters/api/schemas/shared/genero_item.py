from __future__ import annotations

from pydantic import BaseModel


class GeneroItem(BaseModel):
    codigo: str
    nombre: str
