from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.routers import auth_router
from src.adapters.api.schemas.me_response_schema import MeResponse
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion
from src.infrastructure.config.dependencies import (
    get_servicio_sesiones,
    get_sesion_repo,
    get_settings,
)
from src.infrastructure.config.settings import Settings
from src.infrastructure.persistence.database import get_db_session_async
from src.infrastructure.security.jwt_handler import JWTHandler

_RUTA_LOGOUT = "/logout"


async def _sin_db() -> AsyncGenerator[None, None]:
    yield None


def _app(settings: Settings) -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router.router)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db_session_async] = _sin_db
    return app


async def test_logout_cierra_sesion_en_registro_ap0132() -> None:
    # AP-0132: al cerrar sesion, ademas de revocar el jti, la fila del Session Registry
    # queda REVOCADA con motivo LOGOUT y fecha de cierre (descarte del lado servidor).
    settings = Settings()
    servicio = get_servicio_sesiones(settings)
    sid = "sid-logout-0132"
    await servicio.registrar(
        sid=sid,
        uid=1,
        roles=["comisionista"],
        jti="j-0132",
        device_fp="fp",
        ip="127.0.0.1",
        user_agent="pytest",
    )
    assert await servicio.esta_revocada(sid) is False

    jwt = JWTHandler(settings.jwt_secret_key, settings.jwt_algorithm)
    token = jwt.encode(
        {
            "sub": "1",
            "nombre": "1",
            "roles": ["comisionista"],
            "jti": "j-0132",
            "sid": sid,
            "tv": 1,
        },
        expires_minutes=30,
    )
    cliente = TestClient(_app(settings))
    cliente.cookies.set(settings.cookie_auth_name, token)
    resp = cliente.post(_RUTA_LOGOUT)
    assert resp.status_code == 204

    assert await servicio.esta_revocada(sid) is True
    sesion = await get_sesion_repo().obtener(sid)
    assert sesion is not None
    assert sesion.estado.value == "revocada"
    assert sesion.motivo_cierre == MotivoCierreSesion.LOGOUT
    assert sesion.fecha_cierre is not None


def test_me_response_incluye_session_expires_at_ap0132() -> None:
    # AP-0132: el contrato de /auth/me expone el techo de expiracion no secreto que el
    # cliente usa para anticipar el descarte de los datos locales.
    respuesta = MeResponse(
        uid=1,
        username="u",
        email="e@sufi.co",
        roles=[],
        tiene_incentivos=False,
        programa=None,
        session_expires_at="2026-07-14T12:00:00+00:00",
    )
    dumped = respuesta.model_dump()
    assert dumped["session_expires_at"] == "2026-07-14T12:00:00+00:00"