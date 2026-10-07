from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated, Final

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse

from src.adapters.api.object_authz import autorizar_objeto, require_object_access
from src.adapters.api.schemas.asesor_documentos.asesor_documentos_item import (
    AsesorDocumentosItem,
)
from src.adapters.api.schemas.asesor_documentos.asesor_documentos_list_response import (
    AsesorDocumentosListResponse,
)
from src.adapters.api.schemas.documento.documento_edit_request import DocumentoEditRequest
from src.adapters.api.schemas.documento.documento_edit_response import DocumentoEditResponse
from src.adapters.api.schemas.documento_upload_schema import DocumentoUploadRequest
from src.adapters.api.schemas.moderar_documento_schema import ModerarDocumentoRequest
from src.adapters.api.validacion_archivos import (
    EXTENSIONES_DOCUMENTOS,
    MIME_DOCUMENTOS,
    verificar_content_type_archivo,
    verificar_firma_archivo,
    verificar_tamano_contenido,
    verificar_tamano_upload,
    verificar_tipo_permitido,
)
from src.application.dto.asesor_documentos_list_dto import AsesorDocumentosListDTO
from src.application.dto.documento_edit_dto import DocumentoEditDTO
from src.application.dto.documento_upload_dto import DocumentoUploadDTO
from src.application.dto.moderar_documento_dto import ModerarDocumentoDTO
from src.application.services.authorization_service import AuthorizationService
from src.application.use_cases.gestionar_documentos_use_case import GestionarDocumentosUseCase
from src.domain.entities.documento_entity import DocumentoEntity
from src.domain.value_objects.accion_recurso import AccionRecurso
from src.domain.value_objects.permiso import Permiso
from src.domain.value_objects.resource_type import ResourceType
from src.infrastructure.config.dependencies import (
    SanitizadorMetadatosDep,
    SettingsDep,
    TokenDep,
    get_authorization_service,
    get_documentos_uc,
)
from src.infrastructure.config.permission_dependencies import (
    actor_desde_token,
    require_permission,
)
from src.shared.constants.content_types import content_type_por_nombre
from src.shared.constants.tipos_documento import TIPOS_DOCUMENTO_NOMBRES, TIPOS_DOCUMENTO_PREFIJOS

router = APIRouter()

_TIPO_PREFIX: Final[dict[int, str]] = TIPOS_DOCUMENTO_PREFIJOS
_PAGE_SIZE_MAX: Final[int] = 100

# AP-0053 F4: permiso para subir un documento propio (comisionista) o gestionar el
# de un tercero como staff (documentador/asesor/webmaster/administrator).
_DEP_SUBIR_PROPIO_O_STAFF = Depends(
    require_permission(Permiso.DOCUMENTOS_SUBIR_PROPIO, Permiso.DOCUMENTOS_MODERAR)
)
# Operaciones administrativas sobre documentos de CUALQUIER asesor: exclusivas de
# staff con DOCUMENTOS_MODERAR (moderar, listar por asesor, editar, eliminar, servir
# el archivo). Cierra el IDOR de lectura/escritura que exponia estos endpoints a
# cualquier usuario autenticado (AP-0053).
_DEP_STAFF = Depends(require_permission(Permiso.DOCUMENTOS_MODERAR))


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[_DEP_SUBIR_PROPIO_O_STAFF])
async def subir_documento(
    token: TokenDep,
    body: DocumentoUploadRequest,
    authz: AuthorizationService = Depends(get_authorization_service),
    uc: GestionarDocumentosUseCase = Depends(get_documentos_uc),
) -> dict[str, object]:
    await autorizar_objeto(
        authz, token, ResourceType.DOCUMENTO, AccionRecurso.CREATE, body.numero_documento
    )
    dto: DocumentoUploadDTO = DocumentoUploadDTO(
        numero_documento=body.numero_documento,
        tipo=body.tipo,
        nombre=body.nombre,
    )
    entity: DocumentoEntity = await uc.subir_async(dto)
    return {"did": entity.did, "estado": entity.estado}


@router.patch("/moderar", status_code=status.HTTP_200_OK, dependencies=[_DEP_STAFF])
async def moderar_documento(
    token: TokenDep,
    body: ModerarDocumentoRequest,
    authz: AuthorizationService = Depends(get_authorization_service),
    uc: GestionarDocumentosUseCase = Depends(get_documentos_uc),
) -> dict[str, object]:
    await autorizar_objeto(
        authz, token, ResourceType.DOCUMENTO, AccionRecurso.APPROVE, str(body.documento_id)
    )
    actor_uid, _ = actor_desde_token(token)
    dto: ModerarDocumentoDTO = ModerarDocumentoDTO(
        documento_id=body.documento_id,
        estado=body.estado,
        uid_moderador=actor_uid,
        observacion=body.observacion,
    )
    await uc.moderar_async(dto)
    return {"ok": True}


@router.get(
    "/asesores",
    status_code=status.HTTP_200_OK,
    summary="Asesores (paginado) que tienen documentos cargados",
    response_model=AsesorDocumentosListResponse,
    dependencies=[_DEP_STAFF],
)
async def listar_asesores_con_documentos(
    programa: Annotated[int, Query(ge=1, le=2)] = 1,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    cedula: Annotated[str | None, Query(max_length=40)] = None,
    tipo_doc: Annotated[str | None, Query(max_length=10)] = None,
    uc: GestionarDocumentosUseCase = Depends(get_documentos_uc),
) -> AsesorDocumentosListResponse:
    result: AsesorDocumentosListDTO = await uc.listar_asesores_con_documentos_async(
        programa=programa, page=page, page_size=page_size, cedula=cedula, tipo_doc=tipo_doc,
    )
    return AsesorDocumentosListResponse(
        items=[
            AsesorDocumentosItem(
                tipo_documento=item.tipo_documento,
                numero_documento=item.numero_documento,
                email=item.email,
            )
            for item in result.items
        ],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get(
    "/{numero_documento}",
    status_code=status.HTTP_200_OK,
    summary="Documentos de un asesor",
    dependencies=[
        _DEP_STAFF,
        Depends(
            require_object_access(
                ResourceType.DOCUMENTO, AccionRecurso.READ, "numero_documento"
            )
        ),
    ],
)
async def listar_documentos_asesor(
    numero_documento: str,
    uc: GestionarDocumentosUseCase = Depends(get_documentos_uc),
) -> list[dict[str, object]]:
    entities = await uc.listar_por_asesor_async(numero_documento)
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


@router.patch(
    "/{did}",
    status_code=status.HTTP_200_OK,
    summary="Editar documento (estado, fecha, nombre)",
    response_model=DocumentoEditResponse,
    dependencies=[
        _DEP_STAFF,
        Depends(require_object_access(ResourceType.DOCUMENTO, AccionRecurso.UPDATE, "did")),
    ],
)
async def editar_documento(
    did: int,
    body: DocumentoEditRequest,
    uc: GestionarDocumentosUseCase = Depends(get_documentos_uc),
) -> DocumentoEditResponse:
    dto: DocumentoEditDTO = DocumentoEditDTO(
        did=did,
        nombre=body.nombre,
        estado=body.estado,
        fecha=body.fecha,
    )
    try:
        entity: DocumentoEntity | None = await uc.editar_async(dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if entity is None or entity.did is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    return DocumentoEditResponse(
        did=entity.did,
        numero_documento=entity.numero_documento,
        tipo=entity.tipo,
        tipo_nombre=TIPOS_DOCUMENTO_NOMBRES.get(entity.tipo, str(entity.tipo)),
        nombre=entity.nombre,
        estado=entity.estado,
        version=entity.version,
        fecha=entity.fecha,
    )


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Subir archivo PDF de documento",
    dependencies=[_DEP_SUBIR_PROPIO_O_STAFF],
)
async def subir_archivo_documento(
    token: TokenDep,
    settings: SettingsDep,
    sanitizador: SanitizadorMetadatosDep,
    numero_documento: str = Form(...),
    tipo: int = Form(...),
    file: UploadFile = File(...),
    authz: AuthorizationService = Depends(get_authorization_service),
    uc: GestionarDocumentosUseCase = Depends(get_documentos_uc),
) -> dict[str, object]:
    await autorizar_objeto(
        authz, token, ResourceType.DOCUMENTO, AccionRecurso.CREATE, numero_documento
    )
    upload_dir: Path = settings.documentos_path
    prefix: str = _TIPO_PREFIX.get(tipo, str(tipo))
    nombre: str = f"{prefix}{numero_documento}.pdf"
    # AP-0197: el Content-Type de la entrada debe ser el definido (PDF), obligatorio.
    verificar_content_type_archivo(file, MIME_DOCUMENTOS)
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
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest: Path = upload_dir / nombre
    await asyncio.to_thread(dest.write_bytes, content)
    dto: DocumentoUploadDTO = DocumentoUploadDTO(
        numero_documento=numero_documento, tipo=tipo, nombre=nombre
    )
    entity: DocumentoEntity = await uc.subir_async(dto)
    return {
        "did": entity.did,
        "estado": entity.estado,
        "version": entity.version,
        "nombre": entity.nombre,
    }


@router.get(
    "/file/{nombre}",
    summary="Servir PDF de documento (inline)",
    dependencies=[
        _DEP_STAFF,
        Depends(require_object_access(ResourceType.DOCUMENTO, AccionRecurso.DOWNLOAD, "nombre")),
    ],
)
async def servir_archivo_documento(
    nombre: str,
    settings: SettingsDep,
) -> FileResponse:
    safe_name: str = Path(nombre).name
    file_path: Path = settings.documentos_path / safe_name
    if not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")
    return FileResponse(
        path=file_path,
        media_type=content_type_por_nombre(safe_name),
        filename=safe_name,
        headers={"Content-Disposition": f'inline; filename="{safe_name}"'},
    )


@router.delete(
    "/{did}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar documento",
    dependencies=[
        _DEP_STAFF,
        Depends(require_object_access(ResourceType.DOCUMENTO, AccionRecurso.DELETE, "did")),
    ],
)
async def eliminar_documento(
    did: int,
    uc: GestionarDocumentosUseCase = Depends(get_documentos_uc),
) -> dict[str, object]:
    await uc.eliminar_async(did)
    return {"ok": True}
