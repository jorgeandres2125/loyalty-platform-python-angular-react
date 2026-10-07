from __future__ import annotations

from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from src.adapters.api.schemas.reporte.reporte_constants import (
    PAGE_SIZE_MAX,
    PAGE_SIZE_MIN,
    PROGRAMA_MAX,
    PROGRAMA_MIN,
    TIPO_MAX,
    TIPO_MIN,
)


class ReportePreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: Annotated[int, Field(ge=TIPO_MIN, le=TIPO_MAX)]
    programa: Annotated[int, Field(ge=PROGRAMA_MIN, le=PROGRAMA_MAX)] = 1
    subprograma: Annotated[int | None, Field(default=None, ge=0)] = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    cedula: Annotated[str | None, Field(default=None, max_length=40)] = None
    estado: Annotated[int | None, Field(default=None, ge=0, le=3)] = None
    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=PAGE_SIZE_MIN, le=PAGE_SIZE_MAX)] = 10
