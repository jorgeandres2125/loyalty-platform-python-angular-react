from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.routers import (
    admin_usuarios_router,
    asesor_consumo_router,
    asesor_movilidad_router,
    reportes_router,
)
from src.application.dto.reporte_preview_response_dto import ReportePreviewResponseDTO
from src.application.dto.usuario_list_dto import UsuarioListDTO
from src.application.dto.usuario_list_item_dto import UsuarioListItemDTO
from src.domain.value_objects.permiso import Permiso
from src.infrastructure.config.dependencies import (
    get_admin_usuarios_uc,
    get_asesor_consumo_uc,
    get_asesor_movilidad_uc,
    get_preview_reportes_uc,
    get_reportes_uc,
    require_token,
)
from src.infrastructure.config.permission_dependencies import require_permission

SL = chr(47)
_ADMIN = SL + "api" + SL + "v1" + SL + "admin" + SL + "usuarios"
_MOVILIDAD = SL + "api" + SL + "v1" + SL + "asesor-movilidad"
_CONSUMO = SL + "api" + SL + "v1" + SL + "asesor-consumo"
_REPORTES = SL + "api" + SL + "v1" + SL + "reportes"

# AP-0053 F5: pruebas de seguridad end-to-end de los endpoints de mayor riesgo
# identificados en el diagnostico original (R1 gestion de asesores, R5 exportacion
# de reportes, R6 panel administrativo). asesor_movilidad_router, asesor_consumo_router
# y reportes_router NO llevan autorizacion propia: se aplica exclusivamente al
# registrarlos en main.py via include_router(dependencies=[...]). Por eso las
# pruebas replican EXACTAMENTE ese cableado real al montar cada mini-app (probar el
# router aislado, sin esas dependencies, no reflejaria la configuracion desplegada).
# Se reemplaza siempre el caso de uso real por un fake, incluso en los casos 403,
# para que el rechazo dependa unicamente de la capa de autorizacion.


class _FakeAsesorMovilidadUseCase:
    async def listar_async(
        self, page: int, size: int, tipo_doc: str | None = None, documento: str | None = None
    ) -> dict[str, object]:
        return {"items": [], "total": 0, "page": page, "size": size, "pages": 0}

    async def obtener_detalle_async(self, numero_documento: str) -> dict[str, object]:
        return {"contacto": None, "tributario": None, "emocional": None}


class _FakeAsesorConsumoUseCase:
    async def listar_async(
        self, page: int, size: int, tipo_doc: str | None = None, documento: str | None = None
    ) -> dict[str, object]:
        return {"items": [], "total": 0, "page": page, "size": size, "pages": 0}


class _FakeGenerarReportesUseCase:
    async def generar_async(self, dto: object) -> bytes:
        return b"reporte-fake"


class _FakeObtenerPreviewReportesUseCase:
    async def obtener_async(self, dto: object) -> ReportePreviewResponseDTO:
        return ReportePreviewResponseDTO(columns=[], rows=[], total=0, page=1, page_size=10)


class _FakeGestionarUsuariosUseCase:
    async def listar_async(
        self, page: int, page_size: int, texto: str | None, activo: bool | None
    ) -> UsuarioListDTO:
        item = UsuarioListItemDTO(uid=1, nombre="x", email="x@x.com", activo=True, roles=[])
        return UsuarioListDTO(items=[item], total=1, page=page, page_size=page_size)


def _token(uid: str, roles: list[str]) -> dict[str, object]:
    return {"sub": uid, "roles": roles}


def _mini_asesor_movilidad(roles: list[str] | None) -> FastAPI:
    mini = FastAPI()
    mini.include_router(
        asesor_movilidad_router.router,
        prefix=_MOVILIDAD,
        dependencies=[
            Depends(require_token),
            Depends(require_permission(Permiso.MOVILIDAD_ASESORES_GESTIONAR)),
        ],
    )
    if roles is not None:
        mini.dependency_overrides[require_token] = lambda: _token("50", roles)
    mini.dependency_overrides[get_asesor_movilidad_uc] = lambda: _FakeAsesorMovilidadUseCase()
    return mini


def _mini_asesor_consumo(roles: list[str] | None) -> FastAPI:
    mini = FastAPI()
    mini.include_router(
        asesor_consumo_router.router,
        prefix=_CONSUMO,
        dependencies=[
            Depends(require_token),
            Depends(require_permission(Permiso.CONSUMO_ASESORES_GESTIONAR)),
        ],
    )
    if roles is not None:
        mini.dependency_overrides[require_token] = lambda: _token("50", roles)
    mini.dependency_overrides[get_asesor_consumo_uc] = lambda: _FakeAsesorConsumoUseCase()
    return mini


def _mini_reportes(roles: list[str] | None) -> FastAPI:
    mini = FastAPI()
    mini.include_router(
        reportes_router.router,
        prefix=_REPORTES,
        dependencies=[
            Depends(require_token),
            Depends(require_permission(Permiso.REPORTES_EXPORTAR)),
        ],
    )
    if roles is not None:
        mini.dependency_overrides[require_token] = lambda: _token("50", roles)
    mini.dependency_overrides[get_reportes_uc] = lambda: _FakeGenerarReportesUseCase()
    mini.dependency_overrides[get_preview_reportes_uc] = (
        lambda: _FakeObtenerPreviewReportesUseCase()
    )
    return mini


def _mini_admin_usuarios(roles: list[str] | None) -> FastAPI:
    # admin_usuarios_router SI lleva su propia autorizacion (require_admin_usuarios
    # esta declarada en el APIRouter del modulo), asi que se monta sin replicar nada.
    mini = FastAPI()
    mini.include_router(admin_usuarios_router.router, prefix=_ADMIN)
    if roles is not None:
        mini.dependency_overrides[require_token] = lambda: _token("1", roles)
    mini.dependency_overrides[get_admin_usuarios_uc] = lambda: _FakeGestionarUsuariosUseCase()
    return mini


_REPORTE_BODY: dict[str, object] = {"tipo": 5, "programa": 1}


class TestEscalamientoVerticalGestionAsesores:
    """R1 del diagnostico: un comisionista (usuario final) invocando funciones de
    staff que listan o enumeran a TODOS los asesores."""

    def test_comisionista_no_puede_listar_asesores_movilidad_403(self) -> None:
        resp = TestClient(_mini_asesor_movilidad(["comisionista"])).get(_MOVILIDAD)
        assert resp.status_code == 403

    def test_comisionista_no_puede_ver_detalle_de_otro_asesor_movilidad_403(self) -> None:
        resp = TestClient(_mini_asesor_movilidad(["comisionista"])).get(_MOVILIDAD + SL + "999999")
        assert resp.status_code == 403

    def test_staff_si_puede_listar_asesores_movilidad(self) -> None:
        resp = TestClient(_mini_asesor_movilidad(["asesor_comercial"])).get(_MOVILIDAD)
        assert resp.status_code == 200

    def test_comisionista_consumo_no_puede_listar_asesores_consumo_403(self) -> None:
        resp = TestClient(_mini_asesor_consumo(["comisionista_consumo"])).get(_CONSUMO)
        assert resp.status_code == 403

    def test_staff_consumo_si_puede_listar_asesores_consumo(self) -> None:
        resp = TestClient(_mini_asesor_consumo(["asesor_consumo"])).get(_CONSUMO)
        assert resp.status_code == 200

    def test_sin_token_401(self) -> None:
        resp = TestClient(_mini_asesor_movilidad(None)).get(_MOVILIDAD)
        assert resp.status_code == 401


class TestEscalamientoVerticalReportes:
    """R5 del diagnostico: exportacion o preview de reportes (fuga de PII masiva)
    sin permiso."""

    def test_comisionista_no_puede_generar_reporte_403(self) -> None:
        resp = TestClient(_mini_reportes(["comisionista"])).post(
            _REPORTES + SL + "generar", json=_REPORTE_BODY
        )
        assert resp.status_code == 403

    def test_comisionista_no_puede_ver_preview_reporte_403(self) -> None:
        resp = TestClient(_mini_reportes(["comisionista"])).post(
            _REPORTES + SL + "preview", json=_REPORTE_BODY
        )
        assert resp.status_code == 403

    def test_staff_si_puede_generar_reporte(self) -> None:
        resp = TestClient(_mini_reportes(["asesor_comercial"])).post(
            _REPORTES + SL + "generar", json=_REPORTE_BODY
        )
        assert resp.status_code == 200

    def test_sin_token_401(self) -> None:
        resp = TestClient(_mini_reportes(None)).post(_REPORTES + SL + "generar", json=_REPORTE_BODY)
        assert resp.status_code == 401


class TestEscalamientoVerticalPanelAdministrativo:
    """R6 del diagnostico: invocacion de operaciones administrativas por un actor
    sin el rol requerido."""

    def test_comisionista_no_puede_listar_usuarios_403(self) -> None:
        resp = TestClient(_mini_admin_usuarios(["comisionista"])).get(_ADMIN)
        assert resp.status_code == 403

    def test_staff_no_administrador_no_puede_listar_usuarios_403(self) -> None:
        # asesor_comercial gestiona asesores pero NO administra cuentas de usuario.
        resp = TestClient(_mini_admin_usuarios(["asesor_comercial"])).get(_ADMIN)
        assert resp.status_code == 403

    def test_administrator_si_puede_listar_usuarios(self) -> None:
        resp = TestClient(_mini_admin_usuarios(["administrator"])).get(_ADMIN)
        assert resp.status_code == 200

    def test_webmaster_si_puede_listar_usuarios(self) -> None:
        resp = TestClient(_mini_admin_usuarios(["webmaster"])).get(_ADMIN)
        assert resp.status_code == 200

    def test_manipulacion_de_identificador_uid_no_evade_el_guardia_403(self) -> None:
        # Un comisionista intentando emitir una password temporal para OTRO uid
        # (manipulacion de identificador) debe ser rechazado por el guardia de
        # router antes de que el uid del path importe.
        ruta = _ADMIN + SL + "999" + SL + "password-temporal"
        resp = TestClient(_mini_admin_usuarios(["comisionista"])).post(
            ruta, json={"origen": "admin"}
        )
        assert resp.status_code == 403

    def test_sin_token_401(self) -> None:
        resp = TestClient(_mini_admin_usuarios(None)).get(_ADMIN)
        assert resp.status_code == 401
