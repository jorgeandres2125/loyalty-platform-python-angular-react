from __future__ import annotations

import asyncio
from dataclasses import asdict
from pathlib import Path
from typing import Final

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select

from src.adapters.api.schemas.wizard.paso1_contacto_request import Paso1ContactoRequest
from src.adapters.api.schemas.wizard.paso2_tributario_request import Paso2TributarioRequest
from src.adapters.api.schemas.wizard.paso3_emocional_request import Paso3EmocionalRequest
from src.adapters.api.validacion_archivos import (
    EXTENSIONES_DOCUMENTOS,
    MIME_DOCUMENTOS,
    verificar_firma_archivo,
    verificar_tamano_contenido,
    verificar_tamano_upload,
    verificar_tipo_permitido,
)
from src.application.use_cases.gestionar_documentos_use_case import GestionarDocumentosUseCase
from src.application.use_cases.mi_perfil_use_case import MiPerfilUseCase
from src.domain.entities.documento_entity import DocumentoEntity
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.entities.perfil_emocional_entity import PerfilEmocionalEntity
from src.domain.entities.perfil_tributario_entity import PerfilTributarioEntity
from src.domain.exceptions.perfil_no_encontrado import PerfilNoEncontrado
from src.infrastructure.config.dependencies import (
    SanitizadorMetadatosDep,
    SessionDep,
    SettingsDep,
    TokenDep,
    get_documentos_uc,
    get_mi_perfil_uc,
    get_servicio_auditoria,
)
from src.infrastructure.logging.contexto_seguridad import ContextoSeguridad
from src.infrastructure.persistence.models.ciudad_model import CiudadModel
from src.infrastructure.persistence.models.departamento_model import DepartamentoModel
from src.shared.constants.auditoria import (
    ACCION_DOCUMENTO_ELIMINADO,
    ACCION_DOCUMENTO_SUBIDO,
    ACCION_PERFIL_CONTACTO_ACTUALIZADO,
    ACCION_PERFIL_EMOCIONAL_ACTUALIZADO,
    ACCION_PERFIL_TRIBUTARIO_ACTUALIZADO,
    ENTIDAD_DOCUMENTO,
    ENTIDAD_PERFIL_CONTACTO,
    ENTIDAD_PERFIL_EMOCIONAL,
    ENTIDAD_PERFIL_TRIBUTARIO,
)
from src.shared.constants.tipos_documento import TIPOS_DOCUMENTO_NOMBRES, TIPOS_DOCUMENTO_PREFIJOS

router: APIRouter = APIRouter()


def _ip_actual() -> str | None:
    valor: object = ContextoSeguridad.actual().get("ip_publica")
    return str(valor) if valor is not None else None

# Los roles del JWT vienen como `RolUsuario.value` (slug con underscore),
# no con el nombre legacy con espacios.
_ROL_MOVILIDAD: Final[str] = "comisionista"
_ROL_CONSUMO: Final[str] = "comisionista_consumo"
_ROLES_COMISIONISTA: Final[frozenset[str]] = frozenset({_ROL_MOVILIDAD, _ROL_CONSUMO})
# Todos los tipos del catalogo (Cedula, RUT, Contrato y los tributarios EPS, AFP, ARL,
# Prepagada, Vivienda, Pension voluntaria, AFC, Dependientes). El dueno del perfil puede
# gestionar sus propios PDF; el ownership lo resuelve el JWT, no un parametro del cliente.
_TIPOS_DOC_VALIDOS: Final[frozenset[int]] = frozenset(TIPOS_DOCUMENTO_PREFIJOS)


def _uid_de_token(token: dict) -> int:
    try:
        return int(token.get("sub", 0))
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")


def _roles_de_token(token: dict) -> set[str]:
    raw = token.get("roles") or []
    if not isinstance(raw, list):
        return set()
    return {str(rol) for rol in raw}


def _exigir_rol_comisionista(token: dict) -> None:
    if _ROLES_COMISIONISTA.isdisjoint(_roles_de_token(token)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Solo los roles comisionista o comisionista consumo "
                "pueden acceder a este recurso"
            ),
        )


def _exigir_rol_movilidad(token: dict) -> None:
    if _ROL_MOVILIDAD not in _roles_de_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el rol comisionista (Movilidad) puede acceder a este recurso",
        )


# ── Perfil Contacto ──────────────────────────────────────────────────────────

@router.get("/perfil-contacto", summary="Obtener mi perfil de contacto")
async def obtener_mi_perfil_contacto(
    token: TokenDep,
    session: SessionDep,
    uc: MiPerfilUseCase = Depends(get_mi_perfil_uc),
) -> dict:
    _exigir_rol_comisionista(token)
    uid: int = _uid_de_token(token)
    try:
        entity: PerfilContactoEntity | None = await uc.obtener_contacto_async(uid)
    except PerfilNoEncontrado as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if entity is None:
        return {"contacto": None}

    data: dict = asdict(entity)

    # Enriquecer con nombres pre-resueltos para que el frontend no tenga que
    # disparar dos peticiones extra (departamentos + ciudades) en cadena.
    departamento_nombre: str | None = None
    ciudad_nombre: str | None = None
    try:
        if entity.departamento:
            did: int = int(entity.departamento)
            dep_row = await session.execute(
                select(DepartamentoModel.departamento).where(DepartamentoModel.did == did)
            )
            departamento_nombre = dep_row.scalar_one_or_none()
        if entity.ciudad:
            cid: int = int(entity.ciudad)
            ciu_row = await session.execute(
                select(CiudadModel.ciudad).where(CiudadModel.cid == cid)
            )
            ciudad_nombre = ciu_row.scalar_one_or_none()
    except (TypeError, ValueError):
        # Si el valor no es numérico (legacy o ya es nombre), lo dejamos como vino.
        pass

    data["departamento_nombre"] = departamento_nombre
    data["ciudad_nombre"] = ciudad_nombre
    return {"contacto": data}


@router.put("/perfil-contacto", summary="Actualizar mi perfil de contacto")
async def actualizar_mi_perfil_contacto(
    body: Paso1ContactoRequest,
    token: TokenDep,
    uc: MiPerfilUseCase = Depends(get_mi_perfil_uc),
) -> dict:
    _exigir_rol_comisionista(token)
    uid: int = _uid_de_token(token)
    entity: PerfilContactoEntity = PerfilContactoEntity(
        numero_documento="",  # Se sobrescribe en el UC con el del JWT
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
    try:
        guardado: PerfilContactoEntity = await uc.guardar_contacto_async(uid, entity)
    except PerfilNoEncontrado as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_PERFIL_CONTACTO_ACTUALIZADO,
        user_id=uid,
        entidad=ENTIDAD_PERFIL_CONTACTO,
        entidad_id=guardado.numero_documento,
        ip_origen=_ip_actual(),
        detalle={"estado": guardado.estado},
    )
    return {"numero_documento": guardado.numero_documento, "estado": guardado.estado}


# ── Perfil Tributario (solo Movilidad) ───────────────────────────────────────

@router.get("/perfil-tributario", summary="Obtener mi perfil tributario (solo Movilidad)")
async def obtener_mi_perfil_tributario(
    token: TokenDep,
    uc: MiPerfilUseCase = Depends(get_mi_perfil_uc),
) -> dict:
    _exigir_rol_movilidad(token)
    uid: int = _uid_de_token(token)
    try:
        entity: PerfilTributarioEntity | None = await uc.obtener_tributario_async(uid)
    except PerfilNoEncontrado as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {"tributario": asdict(entity) if entity else None}


@router.put("/perfil-tributario", summary="Actualizar mi perfil tributario (solo Movilidad)")
async def actualizar_mi_perfil_tributario(
    body: Paso2TributarioRequest,
    token: TokenDep,
    uc: MiPerfilUseCase = Depends(get_mi_perfil_uc),
) -> dict:
    _exigir_rol_movilidad(token)
    uid: int = _uid_de_token(token)
    entity: PerfilTributarioEntity = PerfilTributarioEntity(**body.model_dump())
    entity.numero_documento = ""  # Se sobrescribe en el UC con el del JWT
    try:
        guardado: PerfilTributarioEntity = await uc.guardar_tributario_async(uid, entity)
    except PerfilNoEncontrado as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_PERFIL_TRIBUTARIO_ACTUALIZADO,
        user_id=uid,
        entidad=ENTIDAD_PERFIL_TRIBUTARIO,
        entidad_id=guardado.numero_documento,
        ip_origen=_ip_actual(),
    )
    return {"numero_documento": guardado.numero_documento}


# ── Perfil Emocional ─────────────────────────────────────────────────────────

@router.get("/perfil-emocional", summary="Obtener mi perfil emocional")
async def obtener_mi_perfil_emocional(
    token: TokenDep,
    uc: MiPerfilUseCase = Depends(get_mi_perfil_uc),
) -> dict:
    _exigir_rol_comisionista(token)
    uid: int = _uid_de_token(token)
    try:
        entity: PerfilEmocionalEntity | None = await uc.obtener_emocional_async(uid)
    except PerfilNoEncontrado as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {"emocional": asdict(entity) if entity else None}


@router.put("/perfil-emocional", summary="Actualizar mi perfil emocional")
async def actualizar_mi_perfil_emocional(
    body: Paso3EmocionalRequest,
    token: TokenDep,
    uc: MiPerfilUseCase = Depends(get_mi_perfil_uc),
) -> dict:
    _exigir_rol_comisionista(token)
    uid: int = _uid_de_token(token)
    entity: PerfilEmocionalEntity = PerfilEmocionalEntity(**body.model_dump())
    entity.numero_documento = ""  # Se sobrescribe en el UC con el del JWT
    try:
        guardado: PerfilEmocionalEntity = await uc.guardar_emocional_async(uid, entity)
    except PerfilNoEncontrado as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_PERFIL_EMOCIONAL_ACTUALIZADO,
        user_id=uid,
        entidad=ENTIDAD_PERFIL_EMOCIONAL,
        entidad_id=guardado.numero_documento,
        ip_origen=_ip_actual(),
    )
    return {"numero_documento": guardado.numero_documento}


# ── Dashboard (agregado: estado del perfil + documentos + datos clave) ─────

@router.get("/dashboard", summary="Mi dashboard (info personalizada por rol)")
async def obtener_mi_dashboard(
    token: TokenDep,
    session: SessionDep,
    uc: MiPerfilUseCase = Depends(get_mi_perfil_uc),
) -> dict:
    _exigir_rol_comisionista(token)
    uid: int = _uid_de_token(token)
    roles: list[str] = sorted(_roles_de_token(token))
    try:
        return await uc.obtener_dashboard_async(uid, roles, session)
    except PerfilNoEncontrado as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# ── Documentos (solo Movilidad: Cédula=4, RUT=5, Contrato=6) ────────────────

@router.get("/documentos", summary="Listar mis documentos (solo Movilidad)")
async def listar_mis_documentos(
    token: TokenDep,
    perfil_uc: MiPerfilUseCase = Depends(get_mi_perfil_uc),
    doc_uc: GestionarDocumentosUseCase = Depends(get_documentos_uc),
) -> list[dict]:
    _exigir_rol_movilidad(token)
    uid: int = _uid_de_token(token)
    numero_documento: str = await perfil_uc.resolver_numero_documento_async(uid)
    entities: list[DocumentoEntity] = await doc_uc.listar_por_asesor_async(numero_documento)
    return [
        {
            "did": entity.did,
            "tipo": entity.tipo,
            "tipo_nombre": TIPOS_DOCUMENTO_NOMBRES.get(entity.tipo, str(entity.tipo)),
            "nombre": entity.nombre,
            "estado": entity.estado,
            "version": entity.version,
            "fecha": entity.fecha.isoformat() if entity.fecha else None,
        }
        for entity in entities
    ]


@router.post(
    "/documentos/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Subir uno de mis documentos (solo Movilidad)",
)
async def subir_mi_documento(
    token: TokenDep,
    settings: SettingsDep,
    sanitizador: SanitizadorMetadatosDep,
    tipo: int = Form(..., description="Tipo del catalogo de documentos (4..14)"),
    file: UploadFile = File(...),
    perfil_uc: MiPerfilUseCase = Depends(get_mi_perfil_uc),
    doc_uc: GestionarDocumentosUseCase = Depends(get_documentos_uc),
) -> dict:
    _exigir_rol_movilidad(token)
    if tipo not in _TIPOS_DOC_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de documento invalido",
        )
    uid: int = _uid_de_token(token)
    numero_documento: str = await perfil_uc.resolver_numero_documento_async(uid)

    prefix: str = TIPOS_DOCUMENTO_PREFIJOS.get(tipo, str(tipo))
    nombre: str = f"{prefix}{numero_documento}.pdf"
    verificar_tamano_upload(file, settings.max_upload_bytes)
    content: bytes = await file.read()
    verificar_tamano_contenido(content, settings.max_upload_bytes)
    verificar_firma_archivo(content, nombre)
    verificar_tipo_permitido(
        file=file,
        contenido=content,
        extensiones_permitidas=EXTENSIONES_DOCUMENTOS,
        mimes_permitidos=MIME_DOCUMENTOS,
    )
    content = sanitizador.sanitizar(content, nombre)
    upload_dir: Path = settings.documentos_path
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest: Path = upload_dir / nombre
    await asyncio.to_thread(dest.write_bytes, content)

    from src.application.dto.documento_upload_dto import DocumentoUploadDTO
    dto: DocumentoUploadDTO = DocumentoUploadDTO(
        numero_documento=numero_documento, tipo=tipo, nombre=nombre
    )
    entity: DocumentoEntity = await doc_uc.subir_async(dto)
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_DOCUMENTO_SUBIDO,
        user_id=uid,
        entidad=ENTIDAD_DOCUMENTO,
        entidad_id=str(entity.did),
        ip_origen=_ip_actual(),
        detalle={"tipo": tipo, "nombre": entity.nombre},
    )
    return {
        "did": entity.did,
        "estado": entity.estado,
        "version": entity.version,
        "nombre": entity.nombre,
    }


@router.delete(
    "/documentos/{did}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar uno de mis documentos (solo Movilidad)",
)
async def eliminar_mi_documento(
    did: int,
    token: TokenDep,
    perfil_uc: MiPerfilUseCase = Depends(get_mi_perfil_uc),
    doc_uc: GestionarDocumentosUseCase = Depends(get_documentos_uc),
) -> dict:
    _exigir_rol_movilidad(token)
    uid: int = _uid_de_token(token)
    numero_documento: str = await perfil_uc.resolver_numero_documento_async(uid)

    # Defensa: que el documento pertenezca al usuario logueado
    mios: list[DocumentoEntity] = await doc_uc.listar_por_asesor_async(numero_documento)
    if not any(doc.did == did for doc in mios):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este documento",
        )
    await doc_uc.eliminar_async(did)
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_DOCUMENTO_ELIMINADO,
        user_id=uid,
        entidad=ENTIDAD_DOCUMENTO,
        entidad_id=str(did),
        ip_origen=_ip_actual(),
    )
    return {"ok": True}
