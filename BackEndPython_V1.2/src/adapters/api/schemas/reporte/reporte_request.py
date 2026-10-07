from __future__ import annotations

from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from src.adapters.api.schemas.reporte.reporte_constants import (
    PROGRAMA_MAX,
    PROGRAMA_MIN,
    TIPO_MAX,
    TIPO_MIN,
)


class ReporteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: Annotated[int, Field(ge=TIPO_MIN, le=TIPO_MAX, description="0=HojaVida, 1=InfoLaboral, 2=PlantillaParticipantes, 3=InfoTributaria, 4=UsuariosMigrados, 5=Default, 6=EstadosPerfiles")]
    programa: Annotated[int, Field(ge=PROGRAMA_MIN, le=PROGRAMA_MAX, description="1=Movilidad, 2=Consumo")] = 1
    subprograma: Annotated[int | None, Field(default=None, ge=0)] = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    cedula: Annotated[str | None, Field(default=None, max_length=40)] = None
    estado: Annotated[int | None, Field(default=None, ge=0, le=3, description="Solo tipo 6: 0=Incompleto, 1=Completo, 2=Pendiente, 3=Todos")] = None
