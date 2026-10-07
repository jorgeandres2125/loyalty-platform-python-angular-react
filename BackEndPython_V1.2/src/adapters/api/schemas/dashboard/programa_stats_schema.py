from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ProgramaStatsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total: int
    activos: int
    incompletos: int
    con_incentivos: int
    nuevos_mes: int
