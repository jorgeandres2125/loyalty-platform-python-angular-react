"""AP-0144: verificacion de sincronizacion con la hora oficial del pais."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.routers import health_router
from src.application.use_cases.verificar_sincronizacion_horaria_use_case import (
    VerificarSincronizacionHorariaUseCase,
)
from src.infrastructure.config.dependencies import (
    get_settings,
    get_verificar_sync_horaria_uc,
)
from src.infrastructure.config.settings import Settings
from src.infrastructure.external.reloj_oficial_http import RelojOficialHttp

SL = chr(47)
_BASE = datetime(2026, 6, 26, 15, 0, 0, tzinfo=UTC)
_URL = "https:" + SL + SL + "x.test" + SL + "dt"
_MIME_JSON = "application" + SL + "json"


class _RelojFijo:
    def __init__(self, momento: datetime) -> None:
        self._m = momento

    async def obtener_hora_oficial_async(self) -> datetime:
        return self._m


class _RelojError:
    async def obtener_hora_oficial_async(self) -> datetime:
        raise httpx.ConnectError("sin red")


# ── Caso de uso ───────────────────────────────────────────────────────────────

async def test_en_sincronia() -> None:
    uc = VerificarSincronizacionHorariaUseCase(
        reloj=_RelojFijo(_BASE + timedelta(seconds=5)), umbral_segundos=60, clock=lambda: _BASE
    )
    estado = await uc.ejecutar_async()
    assert estado.sincronizado is True
    assert estado.desfase_segundos == 5.0


async def test_fuera_de_sincronia() -> None:
    uc = VerificarSincronizacionHorariaUseCase(
        reloj=_RelojFijo(_BASE + timedelta(seconds=120)), umbral_segundos=60, clock=lambda: _BASE
    )
    estado = await uc.ejecutar_async()
    assert estado.sincronizado is False
    assert estado.desfase_segundos == 120.0


# ── Adaptador HTTP ────────────────────────────────────────────────────────────

def _reloj_json(payload: dict) -> RelojOficialHttp:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)
    return RelojOficialHttp(url=_URL, timeout=5, transport=httpx.MockTransport(handler))


def _reloj_texto(cuerpo: str) -> RelojOficialHttp:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=cuerpo)
    return RelojOficialHttp(url=_URL, timeout=5, transport=httpx.MockTransport(handler))


async def test_adapter_parsea_json_con_offset() -> None:
    reloj = _reloj_json({"datetime": "2026-06-26T10:00:00-05:00"})
    momento = await reloj.obtener_hora_oficial_async()
    assert momento.astimezone(UTC) == _BASE


async def test_adapter_parsea_texto_plano() -> None:
    reloj = _reloj_texto("2026-06-26T15:00:00+00:00")
    momento = await reloj.obtener_hora_oficial_async()
    assert momento.astimezone(UTC) == _BASE


async def test_adapter_sin_fecha_reconocible_lanza() -> None:
    reloj = _reloj_json({"foo": "bar"})
    with pytest.raises(ValueError):
        await reloj.obtener_hora_oficial_async()


# ── Endpoint ──────────────────────────────────────────────────────────────────

def _client(uc: object, enabled: bool = True) -> TestClient:
    app = FastAPI()
    app.include_router(health_router.router, prefix=SL + "api" + SL + "v1" + SL + "health")
    app.dependency_overrides[get_settings] = lambda: Settings(hora_sync_enabled=enabled)
    app.dependency_overrides[get_verificar_sync_horaria_uc] = lambda: uc
    return app and TestClient(app)


_RUTA = SL + "api" + SL + "v1" + SL + "health" + SL + "hora"


def test_endpoint_sincronizado() -> None:
    uc = VerificarSincronizacionHorariaUseCase(
        reloj=_RelojFijo(_BASE), umbral_segundos=60, clock=lambda: _BASE
    )
    r = _client(uc).get(_RUTA)
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["verificacion_habilitada"] is True
    assert cuerpo["sincronizado"] is True


def test_endpoint_deshabilitado() -> None:
    uc = VerificarSincronizacionHorariaUseCase(
        reloj=_RelojFijo(_BASE), umbral_segundos=60, clock=lambda: _BASE
    )
    r = _client(uc, enabled=False).get(_RUTA)
    assert r.status_code == 200
    assert r.json()["verificacion_habilitada"] is False


def test_endpoint_degrada_si_falla_api() -> None:
    uc = VerificarSincronizacionHorariaUseCase(reloj=_RelojError(), umbral_segundos=60)
    r = _client(uc).get(_RUTA)
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["sincronizado"] is None
    assert cuerpo["detalle"]
