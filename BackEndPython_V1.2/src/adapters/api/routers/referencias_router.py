from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from src.adapters.api.auditoria_critica import auditar_operacion_critica
from src.adapters.api.schemas.canal_schema import CanalResponse
from src.adapters.api.schemas.ejecutivo_request_schema import EjecutivoRequest
from src.adapters.api.schemas.ejecutivo_response_schema import EjecutivoResponse
from src.adapters.api.schemas.eps.afp_response import AfpResponse
from src.adapters.api.schemas.eps.arl_response import ArlResponse
from src.adapters.api.schemas.eps.banco_response import BancoResponse
from src.adapters.api.schemas.eps.eps_response import EpsResponse
from src.adapters.api.schemas.oficina_schema import OficinaResponse
from src.adapters.api.schemas.profesion_schema import ProfesionResponse
from src.adapters.api.schemas.programa.programa_response import ProgramaResponse
from src.adapters.api.schemas.programa.subprograma_response import SubprogramaResponse
from src.application.dto.ejecutivo_dto import EjecutivoDTO
from src.application.services.servicio_auditoria import ServicioAuditoria
from src.application.use_cases.gestionar_referencias_use_case import GestionarReferenciasUseCase
from src.domain.entities.profesion_entity import ProfesionEntity
from src.domain.value_objects.permiso import Permiso
from src.infrastructure.config.dependencies import (
    TokenDep,
    get_referencias_uc,
    get_servicio_auditoria,
)
from src.infrastructure.config.permission_dependencies import (
    actor_desde_token,
    require_permission,
)

router: APIRouter = APIRouter()


@router.get("/ejecutivos", response_model=list[EjecutivoResponse])
async def listar_ejecutivos(uc: GestionarReferenciasUseCase = Depends(get_referencias_uc)) -> list[EjecutivoResponse]:
    entities = await uc.listar_ejecutivos_async()
    return [
        EjecutivoResponse(
            usuario_asesor=entity.usuario_asesor,
            email_asesor=entity.email_asesor,
            usuario_comisionista=entity.usuario_comisionista,
            email_comisionista=entity.email_comisionista,
            nombre_comisionista=entity.nombre_comisionista,
            fecha_registro=entity.fecha_registro,
        )
        for entity in entities
    ]


@router.post(
    "/ejecutivos",
    response_model=EjecutivoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_GESTIONAR))],
)
async def crear_ejecutivo(
    token: TokenDep,
    body: EjecutivoRequest,
    uc: GestionarReferenciasUseCase = Depends(get_referencias_uc),
    auditoria: ServicioAuditoria = Depends(get_servicio_auditoria),
) -> EjecutivoResponse:
    dto: EjecutivoDTO = EjecutivoDTO(
        usuario_asesor=body.usuario_asesor,
        email_asesor=body.email_asesor,
        usuario_comisionista=body.usuario_comisionista,
        email_comisionista=body.email_comisionista,
        nombre_comisionista=body.nombre_comisionista,
        fecha_registro=body.fecha_registro,
    )
    entity = await uc.crear_ejecutivo_async(dto)
    actor_uid, _roles = actor_desde_token(token)
    await auditar_operacion_critica(
        auditoria, actor_uid, "crear_ejecutivo", "ejecutivo", entity.usuario_asesor
    )
    return EjecutivoResponse(
        usuario_asesor=entity.usuario_asesor,
        email_asesor=entity.email_asesor,
        usuario_comisionista=entity.usuario_comisionista,
        email_comisionista=entity.email_comisionista,
        nombre_comisionista=entity.nombre_comisionista,
        fecha_registro=entity.fecha_registro,
    )


@router.get("/canales", response_model=list[CanalResponse])
async def listar_canales(
    cid: int | None = Query(default=None, description="Filtrar por ciudad (ciudades.cid). Hace JOIN canales_oficinas + oficinas."),
    cpid: int | None = Query(default=None, description="Filtrar por programa (canales.cpid)"),
    cspid: int | None = Query(default=None, description="Filtrar por subprograma (canales.cspid). Aplica ind_activo=1."),
    uc: GestionarReferenciasUseCase = Depends(get_referencias_uc),
) -> list[CanalResponse]:
    if cpid is not None or cspid is not None:
        entities = await uc._referencia_repo.listar_canales_filtrados_async(cpid, cspid)
    elif cid is not None:
        entities = await uc._referencia_repo.listar_canales_por_ciudad_async(cid)
    else:
        entities = await uc._referencia_repo.listar_canales_async()
    return [
        CanalResponse(
            cod_canales=entity.cod_canales,
            nom_canales=entity.nom_canales,
            cpid=entity.cpid,
            cspid=entity.cspid,
            ind_activo=entity.ind_activo,
            id_canales=entity.id_canales,
        )
        for entity in entities
    ]


@router.get("/oficinas", response_model=list[OficinaResponse])
async def listar_oficinas(
    cid: int | None = Query(default=None, description="Filtrar por ciudad (oficinas.cpid = ciudades.cid)"),
    cod_canales: int | None = Query(default=None, description="Filtrar por canal (JOIN canales_oficinas)"),
    cspid: int | None = Query(default=None, description="Filtrar por subprograma (canales.cspid). Requiere cod_canales."),
    uc: GestionarReferenciasUseCase = Depends(get_referencias_uc),
) -> list[OficinaResponse]:
    if cid is None and cod_canales is None:
        entities = await uc._referencia_repo.listar_oficinas_async()
    else:
        entities = await uc._referencia_repo.listar_oficinas_filtradas_async(cid, cod_canales, cspid)
    return [
        OficinaResponse(
            cod_oficinas=entity.cod_oficinas,
            id_oficinas=entity.id_oficinas,
            nom_oficinas=entity.nom_oficinas,
            marca=entity.marca,
            regional=entity.regional,
            cpid=entity.cpid,
            ind_activo=entity.ind_activo,
        )
        for entity in entities
    ]


@router.get("/programas", response_model=list[ProgramaResponse])
async def listar_programas(
    uc: GestionarReferenciasUseCase = Depends(get_referencias_uc),
) -> list[ProgramaResponse]:
    entities = await uc._referencia_repo.listar_programas_async()
    return [ProgramaResponse(cpid=entity.cpid, cp_nombre=entity.cp_nombre) for entity in entities]


@router.get("/subprogramas", response_model=list[SubprogramaResponse])
async def listar_subprogramas(
    cpid: int | None = Query(default=None, description="Filtrar subprogramas por programa (cpid)."),
    uc: GestionarReferenciasUseCase = Depends(get_referencias_uc),
) -> list[SubprogramaResponse]:
    entities = await uc._referencia_repo.listar_subprogramas_async(cpid=cpid)
    return [
        SubprogramaResponse(
            cspid=entity.cspid or 0,
            cspid_nombre=entity.cspid_nombre,
            cpid=entity.cpid,
        )
        for entity in entities
    ]


@router.get("/profesiones", response_model=list[ProfesionResponse])
async def listar_profesiones(
    uc: GestionarReferenciasUseCase = Depends(get_referencias_uc),
) -> list[ProfesionResponse]:
    entities: list[ProfesionEntity] = await uc._referencia_repo.listar_profesiones_async()
    return [
        ProfesionResponse(tid=entity.tid, nombre=entity.nombre)
        for entity in entities
    ]


@router.get("/eps", response_model=list[EpsResponse], summary="Catálogo de EPS")
async def listar_eps(
    uc: GestionarReferenciasUseCase = Depends(get_referencias_uc),
) -> list[EpsResponse]:
    entities = await uc._referencia_repo.listar_eps_async()
    return [EpsResponse(tid=entity.tid, nombre=entity.nombre, nit=entity.nit) for entity in entities]


@router.get("/afp", response_model=list[AfpResponse], summary="Catálogo de AFP / Fondos de pensiones")
async def listar_afp(
    uc: GestionarReferenciasUseCase = Depends(get_referencias_uc),
) -> list[AfpResponse]:
    entities = await uc._referencia_repo.listar_afp_async()
    return [AfpResponse(tid=entity.tid, nombre=entity.nombre, nit=entity.nit) for entity in entities]


@router.get("/arl", response_model=list[ArlResponse], summary="Catálogo de ARL")
async def listar_arl(
    uc: GestionarReferenciasUseCase = Depends(get_referencias_uc),
) -> list[ArlResponse]:
    entities = await uc._referencia_repo.listar_arl_async()
    return [ArlResponse(tid=entity.tid, nombre=entity.nombre, nit=entity.nit) for entity in entities]


@router.get("/bancos", response_model=list[BancoResponse], summary="Catálogo de bancos")
async def listar_bancos(
    uc: GestionarReferenciasUseCase = Depends(get_referencias_uc),
) -> list[BancoResponse]:
    entities = await uc._referencia_repo.listar_bancos_async()
    return [BancoResponse(tid=entity.tid, nombre=entity.nombre, codigo=entity.codigo) for entity in entities]
