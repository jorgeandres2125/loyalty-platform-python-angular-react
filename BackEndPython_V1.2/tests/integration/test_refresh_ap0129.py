from __future__ import annotations

import time

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.routers import auth_router
from src.application.services.auth_service import AuthService
from src.domain.services.politica_inactividad import PoliticaInactividad
from src.infrastructure.config.dependencies import get_auth_service, require_token
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import PasswordHasher

_RUTA = bytes.fromhex("2f72656672657368").decode()
_SEG_ABS = 1800
_SEG_CANAL = 420


def _svc() -> AuthService:
    return AuthService(
        jwt_handler=JWTHandler("test-secret-key-min-32-chars-xxxxx", "HS256"),
        password_hasher=PasswordHasher(),
        jwt_expire_minutes=30,
        politica_inactividad=PoliticaInactividad(
            minutos_canal=7, minutos_otras=20, roles_canal=frozenset({"comisionista"})
        ),
    )


def _app(claims: dict[str, object]) -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router.router)
    app.dependency_overrides[require_token] = lambda: claims
    app.dependency_overrides[get_auth_service] = _svc
    return app


def _claims(abs_exp: int) -> dict[str, object]:
    ahora = int(time.time())
    return {
        "sub": "1",
        "nombre": "1",
        "roles": ["comisionista"],
        "tv": 1,
        "auth_epoch": ahora,
        "amr": ["pwd"],
        "abs_exp": abs_exp,
        "canal": True,
    }


def test_refresh_con_sesion_activa_renueva_token() -> None:
    cliente = TestClient(_app(_claims(int(time.time()) + _SEG_ABS)))
    resp = cliente.post(_RUTA)
    assert resp.status_code == 200
    cuerpo = resp.json()
    assert cuerpo["canal"] is True
    assert abs(int(cuerpo["expira_en_seg"]) - _SEG_CANAL) <= 5
    assert cuerpo["access_token"]


def test_refresh_tras_techo_absoluto_rechaza_401() -> None:
    cliente = TestClient(_app(_claims(int(time.time()) - 10)))
    resp = cliente.post(_RUTA)
    assert resp.status_code == 401
