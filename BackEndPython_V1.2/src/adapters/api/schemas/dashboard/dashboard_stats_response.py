from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.dashboard.programa_stats_schema import ProgramaStatsSchema


class DashboardStatsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    movilidad: ProgramaStatsSchema
    consumo: ProgramaStatsSchema
