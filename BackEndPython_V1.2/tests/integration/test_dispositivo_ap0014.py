from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.routers import dispositivos_router
from src.application.services.servicio_dispositivo import ServicioDispositivo
from src.infrastructure.config.dependencies import get_servicio_dispositivo, require_token
from src.infrastructure.external.in_memory_dispositivo_repo import InMemoryDispositivoRepo

SL = chr(47)


def _servicio(enabled: bool = True) -> ServicioDispositivo:
    return ServicioDispositivo(repo=InMemoryDispositivoRepo(), enabled=enabled)


class TestServicioDispositivo:
    async def test_dispositivo_nuevo_y_conocido(self) -> None:
        svc = _servicio()
        r1 = await svc.registrar_acceso_async(1, "fp-abc", None, "Mozilla Chrome", "1.2.3.4")
        assert r1.es_nuevo is True
        r2 = await svc.registrar_acceso_async(1, "fp-abc", None, "Mozilla Chrome", "1.2.3.4")
        assert r2.es_nuevo is False
        assert r1.device_hash == r2.device_hash
        devs = await svc.listar_por_usuario_async(1)
        assert len(devs) == 1
        assert devs[0].veces_visto == 2

    async def test_fingerprint_distinto_es_nuevo(self) -> None:
        svc = _servicio()
        await svc.registrar_acceso_async(1, "fp-1", None, "UA", "ip")
        r = await svc.registrar_acceso_async(1, "fp-2", None, "UA", "ip")
        assert r.es_nuevo is True
        assert len(await svc.listar_por_usuario_async(1)) == 2

    async def test_fallback_user_agent_y_nombre(self) -> None:
        svc = _servicio()
        r = await svc.registrar_acceso_async(
            1, None, None, "Mozilla Chrome Windows NT 10", "ip"
        )
        assert r.es_nuevo is True
        assert r.device_hash
        assert "Chrome" in r.device_name

    async def test_deshabilitado_no_registra(self) -> None:
        svc = _servicio(enabled=False)
        r = await svc.registrar_acceso_async(1, "fp", None, "UA", "ip")
        assert r.es_nuevo is False
        assert await svc.listar_por_usuario_async(1) == []

    async def test_dispositivos_por_usuario_aislados(self) -> None:
        svc = _servicio()
        await svc.registrar_acceso_async(1, "fp-a", None, "UA", "ip")
        await svc.registrar_acceso_async(2, "fp-a", None, "UA", "ip")
        assert len(await svc.listar_por_usuario_async(1)) == 1
        assert len(await svc.listar_por_usuario_async(2)) == 1


class TestEndpointMisDispositivos:
    def test_lista_dispositivos(self) -> None:
        svc = _servicio()
        asyncio.run(svc.registrar_acceso_async(42, "fp-x", "Mi PC", "UA", "ip"))
        mini = FastAPI()
        mini.include_router(dispositivos_router.router, prefix=SL + "api" + SL + "v1" + SL + "me")
        mini.dependency_overrides[require_token] = lambda: {"sub": "42"}
        mini.dependency_overrides[get_servicio_dispositivo] = lambda: svc
        cliente = TestClient(mini)
        r = cliente.get(SL + "api" + SL + "v1" + SL + "me" + SL + "dispositivos")
        assert r.status_code == 200
        cuerpo = r.json()
        assert len(cuerpo) == 1
        assert cuerpo[0]["device_name"] == "Mi PC"
        assert cuerpo[0]["veces_visto"] == 1
