from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.routers import documentos_router
from src.application.services.authorization_service import AuthorizationService
from src.application.services.ownership_validator import OwnershipValidator
from src.application.services.permission_evaluator import PermissionEvaluator
from src.application.services.servicio_ownership import ServicioOwnership
from src.application.use_cases.gestionar_documentos_use_case import GestionarDocumentosUseCase
from src.domain.entities.documento_entity import DocumentoEntity
from src.domain.value_objects.accion_recurso import AccionRecurso
from src.domain.value_objects.resource_type import ResourceType
from src.infrastructure.config.dependencies import (
    get_authorization_service,
    get_documentos_uc,
    get_settings,
    require_token,
)
from src.infrastructure.config.settings import Settings

SL = chr(47)


class _CapturingAuditor:
    def __init__(self) -> None:
        self.registros: list[tuple[ResourceType, AccionRecurso, str | None, bool]] = []

    async def registrar(
        self,
        actor_uid: int,
        tipo: ResourceType,
        resource_id: str | None,
        accion: AccionRecurso,
        permitido: bool,
        motivo: str,
        modo: str,
    ) -> None:
        self.registros.append((tipo, accion, resource_id, permitido))


class _FakeDocumentoRepo:
    async def obtener_por_documento_tipo_async(
        self, numero_documento: str, tipo: int
    ) -> DocumentoEntity | None:
        return None

    async def obtener_por_did_async(self, did: int) -> DocumentoEntity | None:
        return None

    async def guardar_async(self, entity: DocumentoEntity) -> DocumentoEntity:
        entity.did = 1
        return entity

    async def actualizar_estado_async(self, did: int, estado: str) -> None:
        return None

    async def actualizar_documento_async(
        self, did: int, nombre: str | None, estado: str | None, fecha: datetime | None
    ) -> DocumentoEntity | None:
        return DocumentoEntity(numero_documento="x", did=did, estado=estado or "pendiente")

    async def listar_pendientes_async(self) -> list[DocumentoEntity]:
        return []

    async def listar_por_asesor_async(self, numero_documento: str) -> list[DocumentoEntity]:
        return []

    async def listar_asesores_con_documentos_async(
        self,
        programa: int,
        page: int,
        page_size: int,
        cedula: str | None = None,
        tipo_doc: str | None = None,
    ) -> tuple[list[tuple[str, str, str | None]], int]:
        return [], 0

    async def eliminar_async(self, did: int) -> None:
        return None


def _authz(auditor: _CapturingAuditor) -> AuthorizationService:
    # Las acciones de staff sobre documentos tienen ownership_required=False, por lo
    # que el validator nunca se consulta; se pasan stubs.
    validator = OwnershipValidator(
        servicio_ownership=ServicioOwnership(None),  # type: ignore[arg-type]
        desafio_store=None,  # type: ignore[arg-type]
    )
    return AuthorizationService(
        PermissionEvaluator(), validator, auditor, "enforce"  # type: ignore[arg-type]
    )


def _mini(roles: list[str], auditor: _CapturingAuditor) -> FastAPI:
    mini = FastAPI()
    mini.include_router(documentos_router.router, prefix=SL + "api" + SL + "v1" + SL + "documentos")
    mini.dependency_overrides[require_token] = lambda: {"sub": "50", "roles": roles}
    mini.dependency_overrides[get_settings] = lambda: Settings()
    mini.dependency_overrides[get_documentos_uc] = lambda: GestionarDocumentosUseCase(
        documento_repo=_FakeDocumentoRepo()  # type: ignore[arg-type]
    )
    mini.dependency_overrides[get_authorization_service] = lambda: _authz(auditor)
    return mini


def _doc(sufijo: str) -> str:
    return SL + "api" + SL + "v1" + SL + "documentos" + sufijo


class TestAuditStaffObjetoM3:
    """AP-0055 M3: cada acceso de staff a un documento de un tercero deja traza
    por-objeto (ALLOW) con actor, tipo, id y accion."""

    def test_staff_lee_documento_registra_allow_read(self) -> None:
        aud = _CapturingAuditor()
        resp = TestClient(_mini(["asesor_comercial"], aud)).get(_doc(SL + "999999"))
        assert resp.status_code == 200
        assert (ResourceType.DOCUMENTO, AccionRecurso.READ, "999999", True) in aud.registros

    def test_staff_modera_registra_allow_approve(self) -> None:
        aud = _CapturingAuditor()
        resp = TestClient(_mini(["documentador"], aud)).patch(
            _doc(SL + "moderar"),
            json={"documento_id": 7, "estado": "aprobado", "observacion": ""},
        )
        assert resp.status_code == 200
        assert (ResourceType.DOCUMENTO, AccionRecurso.APPROVE, "7", True) in aud.registros

    def test_staff_elimina_registra_allow_delete(self) -> None:
        aud = _CapturingAuditor()
        resp = TestClient(_mini(["asesor_comercial"], aud)).delete(_doc(SL + "5"))
        assert resp.status_code == 200
        assert (ResourceType.DOCUMENTO, AccionRecurso.DELETE, "5", True) in aud.registros

    def test_staff_descarga_pasa_authz_y_404_por_archivo_faltante(self) -> None:
        # authz permite (staff), pero el archivo no existe -> 404 (NO 403).
        aud = _CapturingAuditor()
        resp = TestClient(_mini(["asesor_comercial"], aud)).get(_doc(SL + "file" + SL + "x.pdf"))
        assert resp.status_code == 404
        assert (ResourceType.DOCUMENTO, AccionRecurso.DOWNLOAD, "x.pdf", True) in aud.registros


class TestComisionistaBloqueadoObjetosDeTerceros:
    """AP-0055/AP-0053: un comisionista no accede a documentos de terceros por id."""

    def test_comisionista_no_lee_documento_de_otro_403(self) -> None:
        aud = _CapturingAuditor()
        resp = TestClient(_mini(["comisionista"], aud)).get(_doc(SL + "999999"))
        assert resp.status_code == 403

    def test_comisionista_no_elimina_documento_403(self) -> None:
        aud = _CapturingAuditor()
        resp = TestClient(_mini(["comisionista"], aud)).delete(_doc(SL + "5"))
        assert resp.status_code == 403

    def test_comisionista_no_descarga_archivo_403(self) -> None:
        aud = _CapturingAuditor()
        resp = TestClient(_mini(["comisionista"], aud)).get(_doc(SL + "file" + SL + "x.pdf"))
        assert resp.status_code == 403
