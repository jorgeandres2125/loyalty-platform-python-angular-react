from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.schemas.admin.usuarios.estado_cuenta_request import EstadoCuentaRequest
from src.adapters.api.schemas.admin.usuarios.usuario_list_item import UsuarioListItem
from src.adapters.api.schemas.asesor_movilidad.asesor_movilidad_item import AsesorMovilidadItem
from src.adapters.api.schemas.asesor_movilidad.asesor_movilidad_list_response import (
    AsesorMovilidadListResponse,
)
from src.adapters.api.schemas.shared.ciudad_item import CiudadItem
from src.adapters.api.schemas.shared.departamento_item import DepartamentoItem
from src.adapters.api.schemas.shared.genero_item import GeneroItem
from src.adapters.api.schemas.shared.programa_item import ProgramaItem
from src.adapters.api.schemas.shared.tipo_documento_item import TipoDocumentoItem
from src.adapters.api.schemas.wizard.paso1_contacto_request import Paso1ContactoRequest
from src.adapters.api.schemas.wizard.paso2_tributario_request import Paso2TributarioRequest
from src.adapters.api.schemas.wizard.paso3_emocional_request import Paso3EmocionalRequest
from src.application.use_cases.asesor_movilidad_use_case import AsesorMovilidadUseCase
from src.application.use_cases.gestionar_usuarios_use_case import GestionarUsuariosUseCase
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.entities.perfil_emocional_entity import PerfilEmocionalEntity
from src.domain.entities.perfil_tributario_entity import PerfilTributarioEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.permiso_denegado import PermisoDenegado
from src.domain.value_objects.rol_usuario import RolUsuario
from src.infrastructure.config.dependencies import get_admin_usuarios_uc, get_asesor_movilidad_uc
from src.infrastructure.config.permission_dependencies import (
    actor_desde_token,
    require_gestion_comisionistas,
)

router: APIRouter = APIRouter()

_TIPO_DOC_NOMBRES: dict[str, str] = {
    "CC": "C.C.",
    "CE": "C.E.",
    "F&I": "F&I",
    "GC": "GC",
    "PEP": "PEP",
    "PPT": "PPT",
    "VDA": "VDA",
}

_GENERO_MAP: dict[str, tuple[str, str]] = {
    "0": ("F", "Femenino"),
    "1": ("M", "Masculino"),
    "F": ("F", "Femenino"),
    "M": ("M", "Masculino"),
    "Femenino": ("F", "Femenino"),
    "Masculino": ("M", "Masculino"),
    "Otro": ("O", "Otro"),
    "O": ("O", "Otro"),
}


@router.get("", response_model=AsesorMovilidadListResponse, summary="Lista paginada de asesores Movilidad")
async def listar_asesores_movilidad(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    tipo_doc: str | None = Query(default=None, description="Código de tipo_documento: VDA, F&I, CC, CE, GC"),
    documento: str | None = Query(default=None, description="Búsqueda parcial por número de documento"),
    uc: AsesorMovilidadUseCase = Depends(get_asesor_movilidad_uc),
) -> AsesorMovilidadListResponse:
    resultado: dict = await uc.listar_async(page, size, tipo_doc=tipo_doc, documento=documento)
    items: list[AsesorMovilidadItem] = [
        AsesorMovilidadItem(
            numero_documento=entity.numero_documento,
            nombre_completo=entity.nombre_completo or None,
            tipo_documento=TipoDocumentoItem(
                codigo=entity.tipo_documento,
                nombre=_TIPO_DOC_NOMBRES.get(entity.tipo_documento, entity.tipo_documento),
            ) if entity.tipo_documento else None,
            genero=GeneroItem(
                codigo=_GENERO_MAP.get(entity.genero or "", (entity.genero or "", entity.genero or ""))[0],
                nombre=_GENERO_MAP.get(entity.genero or "", (entity.genero or "", entity.genero or ""))[1],
            ) if entity.genero else None,
            celular=entity.celular,
            programa=ProgramaItem(cpid=entity.comisionista_programa_id, cp_nombre=entity.cp_nombre) if entity.comisionista_programa_id else None,
            departamento=DepartamentoItem(did=entity.dep_did, pid=entity.dep_pid, departamento=entity.dep_nombre) if entity.dep_did is not None else None,
            ciudad=CiudadItem(cid=entity.ciu_cid, did=entity.ciu_did, ciudad=entity.ciu_nombre) if entity.ciu_cid is not None else None,
            estado=entity.estado,
            fecha_completado=entity.fecha_completado,
            incentivos=entity.incentivos,
        )
        for entity in resultado["items"]
    ]
    return AsesorMovilidadListResponse(
        items=items,
        total=resultado["total"],
        page=resultado["page"],
        size=resultado["size"],
        pages=resultado["pages"],
    )


@router.get("/subprogramas/{cpid}", summary="Subprogramas del programa Movilidad")
async def listar_subprogramas(
    cpid: int,
    uc: AsesorMovilidadUseCase = Depends(get_asesor_movilidad_uc),
) -> list[dict]:
    subs = await uc.listar_subprogramas_async(cpid)
    return [{"cspid": sub.cspid, "cspid_nombre": sub.cspid_nombre, "cpid": sub.cpid} for sub in subs]


@router.get(
    "/verificar/{numero_documento}",
    summary="Verifica si un documento ya tiene perfil de Movilidad",
)
async def verificar_asesor_movilidad(
    numero_documento: str,
    uc: AsesorMovilidadUseCase = Depends(get_asesor_movilidad_uc),
) -> dict:
    return await uc.verificar_async(numero_documento)


@router.get("/{numero_documento}", summary="Detalle del asesor Movilidad")
async def detalle_asesor_movilidad(
    numero_documento: str,
    uc: AsesorMovilidadUseCase = Depends(get_asesor_movilidad_uc),
) -> dict:
    detalle: dict = await uc.obtener_detalle_async(numero_documento)
    contacto: PerfilContactoEntity | None = detalle["contacto"]
    tributario: PerfilTributarioEntity | None = detalle["tributario"]
    emocional: PerfilEmocionalEntity | None = detalle["emocional"]
    return {
        "contacto": asdict(contacto) if contacto else None,
        "tributario": asdict(tributario) if tributario else None,
        "emocional": asdict(emocional) if emocional else None,
    }


@router.post(
    "/wizard/paso1",
    status_code=status.HTTP_201_CREATED,
    summary="Wizard Movilidad — Paso 1: datos de contacto",
)
async def wizard_paso1_movilidad(
    body: Paso1ContactoRequest,
    uc: AsesorMovilidadUseCase = Depends(get_asesor_movilidad_uc),
) -> dict:
    entity: PerfilContactoEntity = PerfilContactoEntity(
        numero_documento=body.numero_documento,
        tipo_documento=body.tipo_documento,
        nombre_completo=body.nombre_completo,
        genero=body.genero,
        fecha_nacimiento=body.fecha_nacimiento,
        celular=body.celular,
        telefono=body.telefono,
        email=body.email,
        direccion=body.direccion,
        departamento=body.departamento,
        ciudad=body.ciudad,
        concesionario=body.concesionario,
        tipo_de_cuenta=body.tipo_de_cuenta,
        banco=body.banco,
        numero_de_cuenta=body.numero_de_cuenta,
        acepto_habeas_data=body.acepto_habeas_data,
        incentivos=body.incentivos,
        estado=body.estado,
        firma_contrato=body.firma_contrato,
        requiere_comision=body.requiere_comision,
        comisionista_programa_id=body.comisionista_programa_id,
        comisionista_subprograma_id=body.comisionista_subprograma_id,
        cod_canales=body.cod_canales,
        cod_oficinas=body.cod_oficinas,
        usuario_responsable=body.usuario_responsable,
    )
    guardado: PerfilContactoEntity = await uc.guardar_paso1_async(entity)
    return {"numero_documento": guardado.numero_documento, "estado": guardado.estado}


@router.post(
    "/wizard/paso2",
    status_code=status.HTTP_200_OK,
    summary="Wizard Movilidad — Paso 2: datos tributarios",
)
async def wizard_paso2_movilidad(
    body: Paso2TributarioRequest,
    uc: AsesorMovilidadUseCase = Depends(get_asesor_movilidad_uc),
) -> dict:
    entity: PerfilTributarioEntity = PerfilTributarioEntity(**body.model_dump())
    guardado: PerfilTributarioEntity = await uc.guardar_paso2_async(entity)
    return {"numero_documento": guardado.numero_documento}


@router.post(
    "/wizard/paso3",
    status_code=status.HTTP_200_OK,
    summary="Wizard Movilidad — Paso 3: perfil emocional",
)
async def wizard_paso3_movilidad(
    body: Paso3EmocionalRequest,
    uc: AsesorMovilidadUseCase = Depends(get_asesor_movilidad_uc),
) -> dict:
    entity: PerfilEmocionalEntity = PerfilEmocionalEntity(**body.model_dump())
    guardado: PerfilEmocionalEntity = await uc.guardar_paso3_async(entity)
    return {"numero_documento": guardado.numero_documento}


@router.post(
    "/wizard/finalizar/{numero_documento}",
    status_code=status.HTTP_200_OK,
    summary="Wizard Movilidad — Finalizar registro (estado=1)",
)
async def wizard_finalizar_movilidad(
    numero_documento: str,
    uc: AsesorMovilidadUseCase = Depends(get_asesor_movilidad_uc),
) -> dict:
    try:
        entity: PerfilContactoEntity = await uc.finalizar_async(numero_documento)
        return {"numero_documento": entity.numero_documento, "estado": entity.estado}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch(
    "/{numero_documento}/estado",
    response_model=UsuarioListItem,
    summary="Habilitar o deshabilitar la cuenta del comisionista Movilidad (AP-0001)",
)
async def cambiar_estado_comisionista_movilidad(
    numero_documento: str,
    body: EstadoCuentaRequest,
    token: dict = Depends(require_gestion_comisionistas),
    uc: GestionarUsuariosUseCase = Depends(get_admin_usuarios_uc),
) -> UsuarioListItem:
    actor_uid: int
    actor_roles: list[RolUsuario]
    actor_uid, actor_roles = actor_desde_token(token)
    try:
        cuenta: UsuarioEntity = await uc.cambiar_estado_por_documento_async(
            numero_documento=numero_documento,
            activo=body.activo,
            actor_uid=actor_uid,
            actor_roles=actor_roles,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermisoDenegado as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UsuarioListItem(
        uid=cuenta.uid if cuenta.uid is not None else 0,
        nombre=cuenta.nombre,
        email=cuenta.email,
        activo=cuenta.activo,
        roles=[rol.value for rol in cuenta.roles],
    )
