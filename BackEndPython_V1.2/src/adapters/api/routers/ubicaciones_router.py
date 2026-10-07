from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from src.adapters.api.schemas.ciudad_schema import CiudadResponse
from src.adapters.api.schemas.departamento_schema import DepartamentoResponse
from src.infrastructure.config.dependencies import SessionDep
from src.infrastructure.persistence.models.ciudad_model import CiudadModel
from src.infrastructure.persistence.models.departamento_model import DepartamentoModel

router = APIRouter()


@router.get("/departamentos", response_model=list[DepartamentoResponse])
async def listar_departamentos(session: SessionDep) -> list[DepartamentoResponse]:
    result = await session.execute(select(DepartamentoModel))
    departamentos: list[DepartamentoResponse] = [
        DepartamentoResponse(did=row.did, pid=row.pid, departamento=row.departamento or "")
        for row in result.scalars().all()
    ]
    return departamentos


@router.get("/ciudades/{departamento_id}", response_model=list[CiudadResponse])
async def listar_ciudades(departamento_id: int, session: SessionDep) -> list[CiudadResponse]:
    result = await session.execute(
        select(CiudadModel).where(CiudadModel.did == departamento_id)
    )
    return [
        CiudadResponse(cid=row.cid, did=row.did, ciudad=row.ciudad or "")
        for row in result.scalars().all()
    ]
