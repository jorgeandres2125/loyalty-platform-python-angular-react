from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.schemas.admin.usuarios.estado_cuenta_request import EstadoCuentaRequest
from src.adapters.api.schemas.admin.usuarios.usuario_list_item import UsuarioListItem
from src.adapters.api.schemas.asesor_consumo.asesor_consumo_item import AsesorConsumoItem
from src.adapters.api.schemas.asesor_consumo.asesor_consumo_list_response import (
    AsesorConsumoListResponse,
)
from src.adapters.api.schemas.asesor_consumo.canales_item import CanalesItem
from src.adapters.api.schemas.asesor_consumo.oficina_item import OficinaItem
from src.adapters.api.schemas.asesor_consumo.subprograma_item import SubprogramaItem
from src.adapters.api.schemas.shared.ciudad_item import CiudadItem
from src.adapters.api.schemas.shared.departamento_item import DepartamentoItem
from src.adapters.api.schemas.shared.genero_item import GeneroItem
from src.adapters.api.schemas.shared.programa_item import ProgramaItem
from src.adapters.api.schemas.shared.tipo_documento_item import TipoDocumentoItem
from src.adapters.api.schemas.wizard.paso1_contacto_request import Paso1ContactoRequest
from src.adapters.api.schemas.wizard.paso3_emocional_request import Paso3EmocionalRequest
from src.application.use_cases.asesor_consumo_use_case import AsesorConsumoUseCase
from src.application.use_cases.gestionar_usuarios_use_case import GestionarUsuariosUseCase
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.entities.perfil_emocional_entity import PerfilEmocionalEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.permiso_denegado import PermisoDenegado
from src.domain.value_objects.rol_usuario import RolUsuario
from src.infrastructure.config.dependencies import get_admin_usuarios_uc, get_asesor_consumo_uc
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


@router.get("", response_model=AsesorConsumoListResponse, summary="Lista paginada de asesores Consumo")
async def listar_asesores_consumo(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    tipo_doc: str | None = Query(default=None, description="Código de tipo_documento: VDA, F&I, CC, CE, GC"),
    documento: str | None = Query(default=None, description="Búsqueda parcial por número de documento"),
    uc: AsesorConsumoUseCase = Depends(get_asesor_consumo_uc),
) -> AsesorConsumoListResponse:
    resultado: dict = await uc.listar_async(page, size, tipo_doc=tipo_doc, documento=documento)
    items: list[AsesorConsumoItem] = [
        AsesorConsumoItem(
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
            canal=CanalesItem(cod_canales=entity.cod_canales, nom_canales=entity.nom_canales) if entity.nom_canales else None,
            oficina=OficinaItem(cod_oficinas=entity.cod_oficinas, id_oficinas=entity.id_oficinas, nom_oficinas=entity.nom_oficinas) if entity.nom_oficinas else None,
            programa=ProgramaItem(cpid=entity.comisionista_programa_id, cp_nombre=entity.cp_nombre) if entity.comisionista_programa_id else None,
            subprograma=SubprogramaItem(cspid=entity.comisionista_subprograma_id, cspid_nombre=entity.cspid_nombre) if entity.cspid_nombre else None,
            departamento=DepartamentoItem(did=entity.dep_did, pid=entity.dep_pid, departamento=entity.dep_nombre) if entity.dep_did is not None else None,
            ciudad=CiudadItem(cid=entity.ciu_cid, did=entity.ciu_did, ciudad=entity.ciu_nombre) if entity.ciu_cid is not None else None,
            estado=entity.estado,
            fecha_completado=entity.fecha_completado,
            incentivos=entity.incentivos,
            email=entity.email,
        )
        for entity in resultado["items"]
    ]
    return AsesorConsumoListResponse(
        items=items,
        total=resultado["total"],
        page=resultado["page"],
        size=resultado["size"],
        pages=resultado["pages"],
    )


@router.get("/subprogramas/{cpid}", summary="Subprogramas del programa Consumo")
async def listar_subprogramas_consumo(
    cpid: int,
    uc: AsesorConsumoUseCase = Depends(get_asesor_consumo_uc),
) -> list[dict]:
    subs = await uc.listar_subprogramas_async(cpid)
    return [{"cspid": sub.cspid, "cspid_nombre": sub.cspid_nombre, "cpid": sub.cpid} for sub in subs]


@router.get(
    "/verificar/{numero_documento}",
    summary="Verifica si un documento ya tiene perfil de Consumo",
)
async def verificar_asesor_consumo(
    numero_documento: str,
    uc: AsesorConsumoUseCase = Depends(get_asesor_consumo_uc),
) -> dict:
    return await uc.verificar_async(numero_documento)


def _contacto_detalle(c: PerfilContactoEntity) -> dict:
    return {
        "numero_documento": c.numero_documento,
        "tipo_documento": TipoDocumentoItem(
            codigo=c.tipo_documento,
            nombre=_TIPO_DOC_NOMBRES.get(c.tipo_documento, c.tipo_documento),
        ).model_dump() if c.tipo_documento else None,
        "nombre_completo": c.nombre_completo,
        "genero": GeneroItem(
            codigo=_GENERO_MAP.get(c.genero or "", (c.genero or "", c.genero or ""))[0],
            nombre=_GENERO_MAP.get(c.genero or "", (c.genero or "", c.genero or ""))[1],
        ).model_dump() if c.genero else None,
        "fecha_nacimiento": c.fecha_nacimiento,
        "telefono": c.telefono,
        "celular": c.celular,
        "direccion": c.direccion,
        "departamento": DepartamentoItem(
            did=c.dep_did, pid=c.dep_pid, departamento=c.dep_nombre or "",
        ).model_dump() if c.dep_did is not None else None,
        "ciudad": CiudadItem(
            cid=c.ciu_cid, did=c.ciu_did, ciudad=c.ciu_nombre or "",
        ).model_dump() if c.ciu_cid is not None else None,
        "concesionario": c.concesionario,
        "tipo_de_cuenta": c.tipo_de_cuenta,
        "banco": c.banco,
        "numero_de_cuenta": c.numero_de_cuenta,
        "acepto_habeas_data": c.acepto_habeas_data,
        "estado": c.estado,
        "fecha_completado": c.fecha_completado,
        "cod_canales": c.cod_canales,
        "cod_oficinas": c.cod_oficinas,
        "comisionista_programa_id": c.comisionista_programa_id,
        "comisionista_subprograma_id": c.comisionista_subprograma_id,
        "requiere_comision": c.requiere_comision,
        "incentivos": c.incentivos,
        "usuario_responsable": c.usuario_responsable,
        "segmentacion": c.segmentacion,
        "firma_contrato": c.firma_contrato,
        "motivo_inactivacion": c.motivo_inactivacion,
        "programa_motivacion": c.programa_motivacion,
        "email": c.email,
        "nom_canales": c.nom_canales,
        "nom_oficinas": c.nom_oficinas,
        "id_oficinas": c.id_oficinas,
        "cp_nombre": c.cp_nombre,
        "cspid_nombre": c.cspid_nombre,
    }


@router.get("/{numero_documento}", summary="Detalle del asesor Consumo")
async def detalle_asesor_consumo(
    numero_documento: str,
    uc: AsesorConsumoUseCase = Depends(get_asesor_consumo_uc),
) -> dict:
    detalle: dict = await uc.obtener_detalle_async(numero_documento)
    contacto: PerfilContactoEntity | None = detalle["contacto"]
    emocional: PerfilEmocionalEntity | None = detalle["emocional"]
    return {
        "contacto": _contacto_detalle(contacto) if contacto else None,
        "emocional": asdict(emocional) if emocional else None,
    }


@router.post(
    "/wizard/paso1",
    status_code=status.HTTP_201_CREATED,
    summary="Wizard Consumo — Paso 1: datos de contacto",
)
async def wizard_paso1_consumo(
    body: Paso1ContactoRequest,
    uc: AsesorConsumoUseCase = Depends(get_asesor_consumo_uc),
) -> dict:
    entity: PerfilContactoEntity = PerfilContactoEntity(
        numero_documento=body.numero_documento,
        tipo_documento=body.tipo_documento,
        nombre_completo=body.nombre_completo,
        genero=body.genero,
        fecha_nacimiento=body.fecha_nacimiento,
        celular=body.celular,
        telefono=body.telefono,
        direccion=body.direccion,
        departamento=body.departamento,
        ciudad=body.ciudad,
        concesionario=body.concesionario,
        tipo_de_cuenta=body.tipo_de_cuenta,
        banco=body.banco,
        numero_de_cuenta=body.numero_de_cuenta,
        acepto_habeas_data=body.acepto_habeas_data,
        comisionista_programa_id=body.comisionista_programa_id,
        comisionista_subprograma_id=body.comisionista_subprograma_id,
        cod_canales=body.cod_canales,
        cod_oficinas=body.cod_oficinas,
        usuario_responsable=body.usuario_responsable,
        email=body.email,
        incentivos=body.incentivos,
        estado=body.estado,
        firma_contrato=body.firma_contrato,
    )
    guardado: PerfilContactoEntity = await uc.guardar_paso1_async(entity)
    return {"numero_documento": guardado.numero_documento, "estado": guardado.estado}


@router.post(
    "/wizard/paso3",
    status_code=status.HTTP_200_OK,
    summary="Wizard Consumo — Paso 3 (final): perfil emocional",
)
async def wizard_paso3_consumo(
    body: Paso3EmocionalRequest,
    uc: AsesorConsumoUseCase = Depends(get_asesor_consumo_uc),
) -> dict:
    entity: PerfilEmocionalEntity = PerfilEmocionalEntity(**body.model_dump())
    guardado: PerfilEmocionalEntity = await uc.guardar_paso3_async(entity)
    return {"numero_documento": guardado.numero_documento}


@router.post(
    "/wizard/finalizar/{numero_documento}",
    status_code=status.HTTP_200_OK,
    summary="Wizard Consumo — Finalizar registro (estado=1)",
)
async def wizard_finalizar_consumo(
    numero_documento: str,
    uc: AsesorConsumoUseCase = Depends(get_asesor_consumo_uc),
) -> dict:
    try:
        entity: PerfilContactoEntity = await uc.finalizar_async(numero_documento)
        return {"numero_documento": entity.numero_documento, "estado": entity.estado}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch(
    "/{numero_documento}/estado",
    response_model=UsuarioListItem,
    summary="Habilitar o deshabilitar la cuenta del comisionista Consumo (AP-0001)",
)
async def cambiar_estado_comisionista_consumo(
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
