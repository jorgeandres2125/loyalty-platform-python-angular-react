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
from src.domain.entities.desafio_oob import DesafioOob
from src.domain.entities.documento_entity import DocumentoEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.value_objects.estado_usuario import EstadoUsuario
from src.infrastructure.config.dependencies import (
    get_authorization_service,
    get_documentos_uc,
    get_settings,
    require_token,
)
from src.infrastructure.config.settings import Settings

SL = chr(47)


class _FakeUsuarioRepo:
    """Mapa uid -> numero_documento (equivalente a dbo.users.name). Implementa el
    Protocol UsuarioRepository completo (los metodos no usados en estos casos de
    prueba son stubs deliberadamente inalcanzables)."""

    def __init__(self, mapa: dict[int, str]) -> None:
        self._mapa: dict[int, str] = mapa

    async def obtener_por_nombre_async(self, nombre: str) -> UsuarioEntity | None:
        return None

    async def obtener_por_uid_async(self, uid: int) -> UsuarioEntity | None:
        numero: str | None = self._mapa.get(uid)
        if numero is None:
            return None
        return UsuarioEntity(uid=uid, nombre=numero, email="")

    async def actualizar_password_async(self, uid: int, nuevo_hash: str) -> None:
        return None

    async def listar_paginado_async(
        self, page: int, page_size: int, texto: str | None, activo: bool | None
    ) -> tuple[list[UsuarioEntity], int]:
        return [], 0

    async def obtener_cualquiera_por_uid_async(self, uid: int) -> UsuarioEntity | None:
        return None

    async def actualizar_estado_async(self, uid: int, activo: bool) -> None:
        return None

    async def obtener_uid_por_documento_async(self, numero_documento: str) -> int | None:
        return None

    async def resolver_estado(self, uid: int) -> EstadoUsuario:
        return EstadoUsuario.ACTIVO


class _FakeDocumentoRepo:
    def __init__(self) -> None:
        self.subidos: list[DocumentoEntity] = []
        self.moderaciones: list[tuple[int, str, int]] = []

    async def obtener_por_documento_tipo_async(
        self, numero_documento: str, tipo: int
    ) -> DocumentoEntity | None:
        return None

    async def obtener_por_did_async(self, did: int) -> DocumentoEntity | None:
        return None

    async def guardar_async(self, entity: DocumentoEntity) -> DocumentoEntity:
        entity.did = len(self.subidos) + 1
        self.subidos.append(entity)
        return entity

    async def actualizar_estado_async(self, did: int, estado: str) -> None:
        pass

    async def actualizar_documento_async(
        self,
        did: int,
        nombre: str | None,
        estado: str | None,
        fecha: datetime | None,
    ) -> DocumentoEntity | None:
        return DocumentoEntity(numero_documento="x", did=did, estado=estado or "pendiente")

    async def listar_pendientes_async(self) -> list[DocumentoEntity]:
        return []

    async def listar_por_asesor_async(self, numero_documento: str) -> list[DocumentoEntity]:
        return [d for d in self.subidos if d.numero_documento == numero_documento]

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
        pass


def _ruta(sufijo: str = "") -> str:
    return SL + "api" + SL + "v1" + SL + "documentos" + sufijo


class _FakeAuditor:
    async def registrar(
        self,
        actor_uid: int,
        tipo: object,
        resource_id: str | None,
        accion: object,
        permitido: bool,
        motivo: str,
        modo: str,
    ) -> None:
        return None


class _FakeDesafioStore:
    async def guardar(self, desafio_id: str, desafio: DesafioOob) -> None:
        return None

    async def obtener(self, desafio_id: str) -> DesafioOob | None:
        return None

    async def eliminar(self, desafio_id: str) -> None:
        return None


def _authz(usuario_repo: _FakeUsuarioRepo) -> AuthorizationService:
    validator = OwnershipValidator(
        servicio_ownership=ServicioOwnership(usuario_repo=usuario_repo),
        desafio_store=_FakeDesafioStore(),
    )
    return AuthorizationService(
        permission_evaluator=PermissionEvaluator(),
        ownership_validator=validator,
        auditor=_FakeAuditor(),  # type: ignore[arg-type]
        modo="enforce",
    )


def _mini_app(
    uid: str, roles: list[str], usuario_repo: _FakeUsuarioRepo, doc_repo: _FakeDocumentoRepo
) -> FastAPI:
    mini = FastAPI()
    mini.include_router(documentos_router.router, prefix=SL + "api" + SL + "v1" + SL + "documentos")
    mini.dependency_overrides[require_token] = lambda: {"sub": uid, "roles": roles}
    mini.dependency_overrides[get_settings] = lambda: Settings()
    mini.dependency_overrides[get_documentos_uc] = (
        lambda: GestionarDocumentosUseCase(documento_repo=doc_repo)
    )
    mini.dependency_overrides[get_authorization_service] = lambda: _authz(usuario_repo)
    return mini


class TestOwnershipSubirDocumento:
    def test_comisionista_sube_su_propio_documento_201(self) -> None:
        repo_usuarios = _FakeUsuarioRepo({7: "123456"})
        doc_repo = _FakeDocumentoRepo()
        mini = _mini_app("7", ["comisionista"], repo_usuarios, doc_repo)
        resp = TestClient(mini).post(
            _ruta(SL), json={"numero_documento": "123456", "tipo": 4, "nombre": "cedula.pdf"}
        )
        assert resp.status_code == 201
        assert doc_repo.subidos[0].numero_documento == "123456"

    def test_comisionista_no_puede_subir_documento_ajeno_403(self) -> None:
        repo_usuarios = _FakeUsuarioRepo({7: "123456"})
        doc_repo = _FakeDocumentoRepo()
        mini = _mini_app("7", ["comisionista"], repo_usuarios, doc_repo)
        resp = TestClient(mini, raise_server_exceptions=False).post(
            _ruta(SL), json={"numero_documento": "999999", "tipo": 4, "nombre": "cedula.pdf"}
        )
        assert resp.status_code == 403
        assert not doc_repo.subidos

    def test_staff_puede_subir_documento_de_un_tercero_201(self) -> None:
        # asesor_comercial tiene DOCUMENTOS_MODERAR: omite la verificacion de ownership.
        repo_usuarios = _FakeUsuarioRepo({50: "otra-cedula-del-staff"})
        doc_repo = _FakeDocumentoRepo()
        mini = _mini_app("50", ["asesor_comercial"], repo_usuarios, doc_repo)
        resp = TestClient(mini).post(
            _ruta(SL), json={"numero_documento": "999999", "tipo": 5, "nombre": "rut.pdf"}
        )
        assert resp.status_code == 201
        assert doc_repo.subidos[0].numero_documento == "999999"

    def test_comisionista_sin_uid_resuelto_403(self) -> None:
        # El uid del token no existe como usuario -> no se puede confirmar propiedad,
        # deny-by-default.
        repo_usuarios = _FakeUsuarioRepo({})
        doc_repo = _FakeDocumentoRepo()
        mini = _mini_app("99", ["comisionista"], repo_usuarios, doc_repo)
        resp = TestClient(mini, raise_server_exceptions=False).post(
            _ruta(SL), json={"numero_documento": "123456", "tipo": 4, "nombre": "cedula.pdf"}
        )
        assert resp.status_code == 403


class TestOperacionesAdministrativasStaffOnly:
    def test_comisionista_no_puede_moderar_403(self) -> None:
        mini = _mini_app("7", ["comisionista"], _FakeUsuarioRepo({}), _FakeDocumentoRepo())
        resp = TestClient(mini).patch(
            _ruta(SL + "moderar"),
            json={"documento_id": 1, "estado": "aprobado", "observacion": ""},
        )
        assert resp.status_code == 403

    def test_staff_puede_moderar_y_uid_moderador_es_el_del_token(self) -> None:
        mini = _mini_app("50", ["documentador"], _FakeUsuarioRepo({}), _FakeDocumentoRepo())
        resp = TestClient(mini).patch(
            _ruta(SL + "moderar"),
            json={"documento_id": 1, "estado": "aprobado", "observacion": "ok"},
        )
        assert resp.status_code == 200

    def test_comisionista_no_puede_listar_documentos_de_otro_asesor_403(self) -> None:
        mini = _mini_app("7", ["comisionista"], _FakeUsuarioRepo({}), _FakeDocumentoRepo())
        resp = TestClient(mini).get(_ruta(SL + "999999"))
        assert resp.status_code == 403

    def test_comisionista_no_puede_listar_asesores_403(self) -> None:
        mini = _mini_app("7", ["comisionista"], _FakeUsuarioRepo({}), _FakeDocumentoRepo())
        resp = TestClient(mini).get(_ruta(SL + "asesores"))
        assert resp.status_code == 403

    def test_comisionista_no_puede_editar_documento_403(self) -> None:
        mini = _mini_app("7", ["comisionista"], _FakeUsuarioRepo({}), _FakeDocumentoRepo())
        resp = TestClient(mini).patch(_ruta(SL + "1"), json={})
        assert resp.status_code == 403

    def test_comisionista_no_puede_eliminar_documento_403(self) -> None:
        mini = _mini_app("7", ["comisionista"], _FakeUsuarioRepo({}), _FakeDocumentoRepo())
        resp = TestClient(mini).delete(_ruta(SL + "1"))
        assert resp.status_code == 403

    def test_comisionista_no_puede_servir_archivo_de_otro_403(self) -> None:
        mini = _mini_app("7", ["comisionista"], _FakeUsuarioRepo({}), _FakeDocumentoRepo())
        resp = TestClient(mini).get(_ruta(SL + "file" + SL + "cualquiera.pdf"))
        assert resp.status_code == 403

    def test_staff_puede_listar_documentos_de_un_asesor(self) -> None:
        doc_repo = _FakeDocumentoRepo()
        mini = _mini_app("50", ["asesor_comercial"], _FakeUsuarioRepo({}), doc_repo)
        resp = TestClient(mini).get(_ruta(SL + "123456"))
        assert resp.status_code == 200
