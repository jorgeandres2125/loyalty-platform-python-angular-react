from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.routers import sapin_router
from src.application.dto.token_sapin_response_dto import TokenSAPINResponseDTO
from src.application.services.authorization_service import AuthorizationService
from src.application.services.ownership_validator import OwnershipValidator
from src.application.services.permission_evaluator import PermissionEvaluator
from src.application.services.servicio_ownership import ServicioOwnership
from src.domain.entities.desafio_oob import DesafioOob
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.value_objects.estado_usuario import EstadoUsuario
from src.infrastructure.config.dependencies import (
    get_authorization_service,
    get_token_sapin_uc,
    require_token,
)

SL = chr(47)
_RUTA = SL + "api" + SL + "v1" + SL + "sapin" + SL + "token"


class _FakeUsuarioRepo:
    """Mapa uid -> numero_documento; Protocol UsuarioRepository completo."""

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


class _FakeTokenSapinUseCase:
    def __init__(self) -> None:
        self.llamadas: list[str] = []

    async def ejecutar_async(self, dto: object) -> TokenSAPINResponseDTO:
        cedula: str = getattr(dto, "cedula")
        self.llamadas.append(cedula)
        return TokenSAPINResponseDTO(token="tok-fake", cedula=cedula, url_sapin="https://sapin")


def _mini_app(uid: str, mapa: dict[int, str], uc: _FakeTokenSapinUseCase) -> FastAPI:
    mini = FastAPI()
    mini.include_router(sapin_router.router, prefix=SL + "api" + SL + "v1" + SL + "sapin")
    mini.dependency_overrides[require_token] = lambda: {"sub": uid, "roles": ["comisionista"]}
    mini.dependency_overrides[get_authorization_service] = lambda: _authz(_FakeUsuarioRepo(mapa))
    mini.dependency_overrides[get_token_sapin_uc] = lambda: uc
    return mini


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


class TestOwnershipTokenSapin:
    """AP-0053 F6: el token SSO de incentivos SAPIN es estrictamente personal — sin
    esta verificacion, cualquier comisionista podia pedir el token de OTRA cedula
    (IDOR hacia la plataforma externa SAPIN, CLAUDE.md la marca como critica)."""

    def test_comisionista_pide_su_propio_token_200(self) -> None:
        uc = _FakeTokenSapinUseCase()
        mini = _mini_app("7", {7: "123456"}, uc)
        resp = TestClient(mini).post(_RUTA, json={"cedula": "123456", "alianza": "alianza-x"})
        assert resp.status_code == 200
        assert resp.json()["cedula"] == "123456"
        assert uc.llamadas == ["123456"]

    def test_comisionista_no_puede_pedir_token_de_otra_cedula_403(self) -> None:
        uc = _FakeTokenSapinUseCase()
        mini = _mini_app("7", {7: "123456"}, uc)
        resp = TestClient(mini, raise_server_exceptions=False).post(
            _RUTA, json={"cedula": "999999", "alianza": "alianza-x"}
        )
        assert resp.status_code == 403
        assert not uc.llamadas

    def test_uid_sin_resolver_deny_by_default_403(self) -> None:
        uc = _FakeTokenSapinUseCase()
        mini = _mini_app("99", {}, uc)
        resp = TestClient(mini, raise_server_exceptions=False).post(
            _RUTA, json={"cedula": "123456", "alianza": "alianza-x"}
        )
        assert resp.status_code == 403
        assert not uc.llamadas
