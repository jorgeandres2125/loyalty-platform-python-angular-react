from __future__ import annotations

from typing import Final

from fastapi import APIRouter
from sqlalchemy import text

from src.adapters.api.schemas.dashboard.dashboard_stats_response import DashboardStatsResponse
from src.adapters.api.schemas.dashboard.programa_stats_schema import ProgramaStatsSchema
from src.infrastructure.config.dependencies import SessionDep

router: APIRouter = APIRouter()

_CPID_MOVILIDAD: Final[int] = 1
_CPID_CONSUMO: Final[int] = 2

_SQL_STATS: Final[str] = """
    SELECT
        comisionista_programa_id,
        COUNT(*)                                                                             AS total,
        SUM(CASE WHEN estado = 1 THEN 1 ELSE 0 END)                                         AS activos,
        SUM(CASE WHEN estado = 0 THEN 1 ELSE 0 END)                                         AS incompletos,
        SUM(CASE WHEN incentivos = 1 THEN 1 ELSE 0 END)                                     AS con_incentivos,
        SUM(
            CASE
                WHEN fecha_completado IS NOT NULL
                 AND YEAR(fecha_completado)  = YEAR(GETDATE())
                 AND MONTH(fecha_completado) = MONTH(GETDATE())
                THEN 1 ELSE 0
            END
        )                                                                                    AS nuevos_mes
    FROM dbo.users_perfil_contacto
    WHERE comisionista_programa_id IN (:cpid_mov, :cpid_con)
    GROUP BY comisionista_programa_id
"""

_EMPTY: Final[ProgramaStatsSchema] = ProgramaStatsSchema(
    total=0, activos=0, incompletos=0, con_incentivos=0, nuevos_mes=0
)


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(session: SessionDep) -> DashboardStatsResponse:
    result = await session.execute(
        text(_SQL_STATS),
        {"cpid_mov": _CPID_MOVILIDAD, "cpid_con": _CPID_CONSUMO},
    )
    by_program: dict[int, ProgramaStatsSchema] = {}
    for row in result.mappings().all():
        cpid: int = int(row["comisionista_programa_id"])
        by_program[cpid] = ProgramaStatsSchema(
            total=int(row["total"]),
            activos=int(row["activos"]),
            incompletos=int(row["incompletos"]),
            con_incentivos=int(row["con_incentivos"]),
            nuevos_mes=int(row["nuevos_mes"]),
        )
    return DashboardStatsResponse(
        movilidad=by_program.get(_CPID_MOVILIDAD, _EMPTY),
        consumo=by_program.get(_CPID_CONSUMO, _EMPTY),
    )
