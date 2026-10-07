from __future__ import annotations

from datetime import datetime

from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from src.adapters.api.main import app as app_real
from src.adapters.api.routers import (
    canales_router,
    ejecutivos_router,
    oficinas_router,
    referencias_router,
)
from src.application.dto.ejecutivo_dto import EjecutivoDTO
from src.application.dto.ejecutivo_form_dto import EjecutivoFormDTO
from src.domain.entities.canal_entity import CanalEntity
from src.domain.entities.ejecutivo_entity import EjecutivoEntity
from src.domain.entities.oficina_entity import OficinaEntity
from src.domain.value_objects.permiso import Permiso
from src.infrastructure.config.dependencies import (
    get_canales_uc,
    get_ejecutivos_uc,
    get_oficinas_uc,
    get_referencias_uc,
    get_servicio_auditoria,
    require_token,
)
from src.infrastructure.config.permission_dependencies import require_permission

# AP-0060: diagnostico encontro que canales_router, oficinas_router y el POST
# de "referencias ejecutivos" quedaban registrados en main.py SOLO con
# CATALOGOS_REFERENCIA_VER (permiso de lectura que posee TODO rol autenticado,
# incluidos comisionista y comisionista_consumo) -- cualquier usuario final podia
# mutar catalogos de referencia y crear "ejecutivos". Se introdujo
# CATALOGOS_REFERENCIA_GESTIONAR (escritura, solo staff y administracion)
# declarado POR RUTA en las mutaciones. Estas pruebas replican el cableado REAL
# de main.py (mismo patron de test_seguridad_endpoints_ap0053.py), no el router
# aislado.

SL = chr(47)
_CANALES = SL + "api" + SL + "v1" + SL + "canales"
_OFICINAS = SL + "api" + SL + "v1" + SL + "oficinas"
_REFERENCIAS = SL + "api" + SL + "v1" + SL + "referencias"
_EJECUTIVOS = SL + "api" + SL + "v1" + SL + "ejecutivos"


def _token(uid: str, roles: list[str]) -> dict[str, object]:
    return {"sub": uid, "roles": roles}


class _FakeAuditoria:
    def __init__(self) -> None:
        self.registros: list[tuple[str, int, str, str]] = []

    async def registrar_async(self, **kwargs: object) -> None:
        user_id_raw = kwargs.get("user_id")
        user_id = int(user_id_raw) if isinstance(user_id_raw, int) else 0
        self.registros.append(
            (
                str(kwargs.get("accion")),
                user_id,
                str(kwargs.get("entidad")),
                str(kwargs.get("entidad_id")),
            )
        )


class _FakeCanalesUseCase:
    async def crear_async(self, dto: object) -> CanalEntity:
        return CanalEntity(cod_canales=1, nom_canales="Canal X", ind_activo=True)

    async def actualizar_async(self, cod_canales: int, dto: object) -> CanalEntity | None:
        return CanalEntity(cod_canales=cod_canales, nom_canales="Canal X", ind_activo=True)


class _FakeOficinasUseCase:
    async def crear_async(self, dto: object) -> OficinaEntity:
        return OficinaEntity(cod_oficinas=1, nom_oficinas="Oficina X", ind_activo=True)

    async def actualizar_async(self, cod_oficinas: int, dto: object) -> OficinaEntity | None:
        return OficinaEntity(cod_oficinas=cod_oficinas, nom_oficinas="Oficina X", ind_activo=True)


class _FakeEjecutivosUseCase:
    async def crear_async(self, dto: EjecutivoFormDTO) -> EjecutivoEntity:
        return EjecutivoEntity(id=1, numero_documento="123", nombre_completo="X", perfil="p")

    async def actualizar_async(
        self, ejecutivo_id: int, dto: EjecutivoFormDTO
    ) -> EjecutivoEntity | None:
        return EjecutivoEntity(
            id=ejecutivo_id, numero_documento="123", nombre_completo="X", perfil="p"
        )


class _FakeReferenciaEjecutivo:
    usuario_asesor = "asesor1"
    email_asesor = ""
    usuario_comisionista = ""
    email_comisionista = ""
    nombre_comisionista = ""
    fecha_registro: datetime | None = None


class _FakeReferenciasUseCase:
    async def crear_ejecutivo_async(self, dto: EjecutivoDTO) -> _FakeReferenciaEjecutivo:
        return _FakeReferenciaEjecutivo()


def _mini_canales(roles: list[str] | None, auditoria: _FakeAuditoria) -> FastAPI:
    mini = FastAPI()
    mini.include_router(
        canales_router.router,
        prefix=_CANALES,
        dependencies=[
            Depends(require_token),
            Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_VER)),
        ],
    )
    if roles is not None:
        mini.dependency_overrides[require_token] = lambda: _token("50", roles)
    mini.dependency_overrides[get_canales_uc] = lambda: _FakeCanalesUseCase()
    mini.dependency_overrides[get_servicio_auditoria] = lambda: auditoria
    return mini


def _mini_oficinas(roles: list[str] | None, auditoria: _FakeAuditoria) -> FastAPI:
    mini = FastAPI()
    mini.include_router(
        oficinas_router.router,
        prefix=_OFICINAS,
        dependencies=[
            Depends(require_token),
            Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_VER)),
        ],
    )
    if roles is not None:
        mini.dependency_overrides[require_token] = lambda: _token("50", roles)
    mini.dependency_overrides[get_oficinas_uc] = lambda: _FakeOficinasUseCase()
    mini.dependency_overrides[get_servicio_auditoria] = lambda: auditoria
    return mini


def _mini_referencias(roles: list[str] | None, auditoria: _FakeAuditoria) -> FastAPI:
    mini = FastAPI()
    mini.include_router(
        referencias_router.router,
        prefix=_REFERENCIAS,
        dependencies=[
            Depends(require_token),
            Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_VER)),
        ],
    )
    if roles is not None:
        mini.dependency_overrides[require_token] = lambda: _token("50", roles)
    mini.dependency_overrides[get_referencias_uc] = lambda: _FakeReferenciasUseCase()
    mini.dependency_overrides[get_servicio_auditoria] = lambda: auditoria
    return mini


def _mini_ejecutivos(roles: list[str] | None, auditoria: _FakeAuditoria) -> FastAPI:
    mini = FastAPI()
    mini.include_router(
        ejecutivos_router.router,
        prefix=_EJECUTIVOS,
        dependencies=[
            Depends(require_token),
            Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_GESTIONAR)),
        ],
    )
    if roles is not None:
        mini.dependency_overrides[require_token] = lambda: _token("50", roles)
    mini.dependency_overrides[get_ejecutivos_uc] = lambda: _FakeEjecutivosUseCase()
    mini.dependency_overrides[get_servicio_auditoria] = lambda: auditoria
    return mini


_CANAL_BODY: dict[str, object] = {"nom_canales": "Canal X"}
_OFICINA_BODY: dict[str, object] = {"nom_oficinas": "Oficina X"}
_EJECUTIVO_REF_BODY: dict[str, object] = {"usuario_asesor": "asesor1"}
_EJECUTIVO_FORM_BODY: dict[str, object] = {
    "tipo_documento": "CC",
    "numero_documento": "123",
    "nombre_completo": "X",
    "codigo_ejecutivo": "E1",
    "email": "x@x.com",
    "perfil": "movilidad",
}


class TestEscalamientoVerticalCatalogosCriticos:
    """AP-0060: un comisionista (usuario final, solo tiene CATALOGOS_REFERENCIA_VER)
    no puede mutar canales, oficinas ni crear ejecutivos -- antes del fix, si podia."""

    def test_comisionista_no_crea_canal(self) -> None:
        auditoria = _FakeAuditoria()
        client = TestClient(_mini_canales(["comisionista"], auditoria))
        resp = client.post(_CANALES, json=_CANAL_BODY)
        assert resp.status_code == 403
        assert auditoria.registros == []

    def test_comisionista_no_actualiza_canal(self) -> None:
        auditoria = _FakeAuditoria()
        client = TestClient(_mini_canales(["comisionista"], auditoria))
        resp = client.put(_CANALES + SL + "1", json=_CANAL_BODY)
        assert resp.status_code == 403

    def test_comisionista_no_crea_oficina(self) -> None:
        auditoria = _FakeAuditoria()
        client = TestClient(_mini_oficinas(["comisionista_consumo"], auditoria))
        resp = client.post(_OFICINAS, json=_OFICINA_BODY)
        assert resp.status_code == 403

    def test_comisionista_no_actualiza_oficina(self) -> None:
        auditoria = _FakeAuditoria()
        client = TestClient(_mini_oficinas(["comisionista"], auditoria))
        resp = client.put(_OFICINAS + SL + "1", json=_OFICINA_BODY)
        assert resp.status_code == 403

    def test_comisionista_no_crea_ejecutivo_via_referencias(self) -> None:
        auditoria = _FakeAuditoria()
        client = TestClient(_mini_referencias(["comisionista"], auditoria))
        resp = client.post(_REFERENCIAS + SL + "ejecutivos", json=_EJECUTIVO_REF_BODY)
        assert resp.status_code == 403
        assert auditoria.registros == []

    def test_comisionista_no_crea_ejecutivo_via_ejecutivos_router(self) -> None:
        auditoria = _FakeAuditoria()
        client = TestClient(_mini_ejecutivos(["comisionista"], auditoria))
        resp = client.post(_EJECUTIVOS, json=_EJECUTIVO_FORM_BODY)
        assert resp.status_code == 403

    def test_sin_token_401(self) -> None:
        auditoria = _FakeAuditoria()
        client = TestClient(_mini_canales(None, auditoria))
        resp = client.post(_CANALES, json=_CANAL_BODY)
        assert resp.status_code == 401


class TestAccesoLegitimoStaffYAdmin:
    """El fix no debe romper el acceso legitimo de staff y administracion."""

    def test_staff_crea_canal_y_queda_auditado(self) -> None:
        auditoria = _FakeAuditoria()
        client = TestClient(_mini_canales(["asesor_comercial"], auditoria))
        resp = client.post(_CANALES, json=_CANAL_BODY)
        assert resp.status_code == 201
        assert auditoria.registros == [("crear_canal", 50, "canal", "1")]

    def test_staff_actualiza_oficina_y_queda_auditado(self) -> None:
        auditoria = _FakeAuditoria()
        client = TestClient(_mini_oficinas(["asesor_comercial"], auditoria))
        resp = client.put(_OFICINAS + SL + "7", json=_OFICINA_BODY)
        assert resp.status_code == 200
        assert auditoria.registros == [("actualizar_oficina", 50, "oficina", "7")]

    def test_administrator_crea_ejecutivo_via_referencias_y_queda_auditado(self) -> None:
        auditoria = _FakeAuditoria()
        client = TestClient(_mini_referencias(["administrator"], auditoria))
        resp = client.post(_REFERENCIAS + SL + "ejecutivos", json=_EJECUTIVO_REF_BODY)
        assert resp.status_code == 201
        assert auditoria.registros == [("crear_ejecutivo", 50, "ejecutivo", "asesor1")]

    def test_webmaster_crea_ejecutivo_via_ejecutivos_router_y_queda_auditado(self) -> None:
        auditoria = _FakeAuditoria()
        client = TestClient(_mini_ejecutivos(["webmaster"], auditoria))
        resp = client.post(_EJECUTIVOS, json=_EJECUTIVO_FORM_BODY)
        assert resp.status_code == 201
        assert auditoria.registros == [("crear_ejecutivo", 50, "ejecutivo", "1")]


# --- Guard de cobertura: las mutaciones de catalogos deben declarar el permiso de
# escritura POR RUTA, no solo el permiso de lectura a nivel de router. Complementa
# el guard generico de AP-0053 (test_rbac_cobertura.py) con una verificacion
# especifica de que estas operaciones criticas no queden solo con VER.

_MUTACIONES_CRITICAS: frozenset[tuple[str, str]] = frozenset(
    {
        ("POST", SL + "api" + SL + "v1" + SL + "canales"),
        ("PUT", SL + "api" + SL + "v1" + SL + "canales" + SL + "{cod_canales}"),
        ("POST", SL + "api" + SL + "v1" + SL + "oficinas"),
        ("PUT", SL + "api" + SL + "v1" + SL + "oficinas" + SL + "{cod_oficinas}"),
        ("POST", SL + "api" + SL + "v1" + SL + "referencias" + SL + "ejecutivos"),
        ("POST", SL + "api" + SL + "v1" + SL + "ejecutivos"),
        ("PUT", SL + "api" + SL + "v1" + SL + "ejecutivos" + SL + "{ejecutivo_id}"),
    }
)


def _permisos_declarados(route: APIRoute) -> list[Permiso]:
    encontrados: list[Permiso] = []
    for dep in route.dependant.dependencies:
        closure = getattr(dep.call, "__closure__", None)
        if not closure:
            continue
        for celda in closure:
            valor = celda.cell_contents
            if isinstance(valor, Permiso):
                encontrados.append(valor)
            elif isinstance(valor, (tuple, frozenset, set, list)):
                encontrados.extend(v for v in valor if isinstance(v, Permiso))
    return encontrados


def test_mutaciones_de_catalogos_exigen_permiso_de_escritura() -> None:
    """Guard AP-0060: cada mutacion critica de catalogos debe declarar
    CATALOGOS_REFERENCIA_GESTIONAR por ruta, no solo CATALOGOS_REFERENCIA_VER."""
    sin_permiso_escritura: list[str] = []
    for route in app_real.routes:
        if not isinstance(route, APIRoute):
            continue
        for metodo in route.methods:
            if (metodo, route.path) not in _MUTACIONES_CRITICAS:
                continue
            if Permiso.CATALOGOS_REFERENCIA_GESTIONAR not in _permisos_declarados(route):
                sin_permiso_escritura.append(f"{metodo} {route.path}")
    assert not sin_permiso_escritura, (
        "Mutaciones criticas de catalogos sin CATALOGOS_REFERENCIA_GESTIONAR (AP-0060): "
        + str(sin_permiso_escritura)
    )


def test_todas_las_mutaciones_criticas_fueron_verificadas() -> None:
    """Asegura que el guard anterior realmente inspecciono las 7 rutas esperadas
    (evita que un cambio de path deje el guard verificando cero rutas en silencio)."""
    vistas: set[tuple[str, str]] = set()
    for route in app_real.routes:
        if not isinstance(route, APIRoute):
            continue
        for metodo in route.methods:
            if (metodo, route.path) in _MUTACIONES_CRITICAS:
                vistas.add((metodo, route.path))
    assert vistas == _MUTACIONES_CRITICAS
