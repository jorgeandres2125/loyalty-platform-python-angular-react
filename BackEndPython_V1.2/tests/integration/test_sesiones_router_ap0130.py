from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.routers import sesiones_router
from src.application.services.servicio_sesiones import ServicioSesiones
from src.domain.services.politica_sesiones import PoliticaSesiones
from src.infrastructure.config.dependencies import get_servicio_sesiones, require_token
from src.infrastructure.external.in_memory_sesion_repo import InMemorySesionRepo

_RUTA_LISTA = bytes.fromhex("2f736573696f6e6573").decode()
_RUTA_ITEM_S1 = bytes.fromhex("2f736573696f6e65732f7331").decode()
_RUTA_OTRAS = bytes.fromhex("2f736573696f6e65732f6365727261722d6f74726173").decode()


def _servicio(max_canal: int = 0) -> ServicioSesiones:
    politica = PoliticaSesiones(max_canal=max_canal, max_otras=0, roles_canal=frozenset())
    return ServicioSesiones(repo=InMemorySesionRepo(), politica=politica, habilitado=True)


def _app(uid: int, sid_actual: str, servicio: ServicioSesiones) -> FastAPI:
    app = FastAPI()
    app.include_router(sesiones_router.router)
    app.dependency_overrides[require_token] = lambda: {
        "sub": str(uid),
        "sid": sid_actual,
    }
    app.dependency_overrides[get_servicio_sesiones] = lambda: servicio
    return app


async def _registrar(servicio: ServicioSesiones, sid: str, uid: int = 1) -> None:
    await servicio.registrar(
        sid=sid,
        uid=uid,
        roles=[],
        jti=f"jti-{sid}",
        device_fp="fp",
        ip="127.0.0.1",
        user_agent="pytest",
    )


async def test_listar_sesiones_marca_la_actual() -> None:
    servicio = _servicio()
    await _registrar(servicio, "s1", uid=1)
    await _registrar(servicio, "s2", uid=1)
    cliente = TestClient(_app(uid=1, sid_actual="s1", servicio=servicio))
    resp = cliente.get(_RUTA_LISTA)
    assert resp.status_code == 200
    cuerpo = resp.json()
    assert len(cuerpo) == 2
    por_sid = {fila["sid"]: fila for fila in cuerpo}
    assert por_sid["s1"]["es_actual"] is True
    assert por_sid["s2"]["es_actual"] is False


async def test_listar_sesiones_vacio_sin_sesiones() -> None:
    servicio = _servicio()
    cliente = TestClient(_app(uid=1, sid_actual="s1", servicio=servicio))
    resp = cliente.get(_RUTA_LISTA)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_cerrar_sesion_propia_204() -> None:
    servicio = _servicio()
    await _registrar(servicio, "s1", uid=1)
    cliente = TestClient(_app(uid=1, sid_actual="s2", servicio=servicio))
    resp = cliente.delete(_RUTA_ITEM_S1)
    assert resp.status_code == 204
    assert await servicio.esta_revocada("s1") is True


async def test_cerrar_sesion_de_otro_usuario_404() -> None:
    servicio = _servicio()
    await _registrar(servicio, "s1", uid=99)
    cliente = TestClient(_app(uid=1, sid_actual="s2", servicio=servicio))
    resp = cliente.delete(_RUTA_ITEM_S1)
    assert resp.status_code == 404
    assert await servicio.esta_revocada("s1") is False


async def test_cerrar_sesion_inexistente_404() -> None:
    servicio = _servicio()
    cliente = TestClient(_app(uid=1, sid_actual="s2", servicio=servicio))
    resp = cliente.delete(_RUTA_ITEM_S1)
    assert resp.status_code == 404


async def test_cerrar_otras_sesiones_deja_solo_la_actual() -> None:
    servicio = _servicio(max_canal=5)
    await _registrar(servicio, "s1", uid=1)
    await _registrar(servicio, "s2", uid=1)
    await _registrar(servicio, "s3", uid=1)
    cliente = TestClient(_app(uid=1, sid_actual="s2", servicio=servicio))
    resp = cliente.post(_RUTA_OTRAS)
    assert resp.status_code == 204
    activas = await servicio.listar(1)
    assert {s.sid for s in activas} == {"s2"}
