from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.main import app as app_real
from src.adapters.api.routers import auditoria_router
from src.application.services.servicio_auditoria import ServicioAuditoria
from src.application.use_cases.consultar_mi_historial_use_case import (
    ConsultarMiHistorialUseCase,
)
from src.domain.entities.registro_auditoria import RegistroAuditoria
from src.domain.value_objects.filtro_auditoria import FiltroAuditoria
from src.infrastructure.config.dependencies import (
    get_consultar_mi_historial_uc,
    require_token,
)
from src.infrastructure.external.in_memory_auditoria_repo import InMemoryAuditoriaRepo
from src.shared.constants.auditoria import (
    ACCION_LOGIN_EXITOSO,
    ACCION_PERFIL_CONTACTO_ACTUALIZADO,
)

SL = chr(47)


def _reg(user_id, accion, creado_iso):
    return RegistroAuditoria(accion=accion, user_id=user_id, creado_iso=creado_iso)


class _EscritorQueFalla:
    async def guardar_async(self, registro):
        raise RuntimeError("fallo simulado de persistencia")


class TestServicioAuditoria:
    async def test_registra_via_escritor(self):
        inmem = InMemoryAuditoriaRepo()
        servicio = ServicioAuditoria(escritor=inmem)
        await servicio.registrar_async(accion=ACCION_LOGIN_EXITOSO, user_id=7, ip_origen="1.2.3.4")
        regs = await inmem.listar_por_usuario_async(7, FiltroAuditoria(page=1, page_size=10))
        assert len(regs) == 1
        assert regs[0].accion == ACCION_LOGIN_EXITOSO
        assert regs[0].creado_iso

    async def test_fail_safe_no_propaga(self):
        servicio = ServicioAuditoria(escritor=_EscritorQueFalla())
        await servicio.registrar_async(accion=ACCION_LOGIN_EXITOSO, user_id=7)

    async def test_serializa_detalle(self):
        inmem = InMemoryAuditoriaRepo()
        servicio = ServicioAuditoria(escritor=inmem)
        await servicio.registrar_async(accion="X", user_id=1, detalle={"estado": 3})
        regs = await inmem.listar_por_usuario_async(1, FiltroAuditoria(page=1, page_size=10))
        assert regs[0].detalle is not None
        assert "estado" in regs[0].detalle


class TestInMemoryRepo:
    async def _repo(self):
        repo = InMemoryAuditoriaRepo()
        await repo.guardar_async(_reg(1, "A", "2026-07-01T10:00:00.000+00:00"))
        await repo.guardar_async(_reg(1, "B", "2026-07-02T10:00:00.000+00:00"))
        await repo.guardar_async(_reg(1, "A", "2026-07-03T10:00:00.000+00:00"))
        await repo.guardar_async(_reg(2, "A", "2026-07-01T10:00:00.000+00:00"))
        return repo

    async def test_solo_del_usuario(self):
        repo = await self._repo()
        filtro = FiltroAuditoria(page=1, page_size=10)
        assert await repo.contar_por_usuario_async(1, filtro) == 3
        assert await repo.contar_por_usuario_async(2, filtro) == 1
        regs = await repo.listar_por_usuario_async(2, filtro)
        assert all(reg.user_id == 2 for reg in regs)

    async def test_orden_descendente(self):
        repo = await self._repo()
        regs = await repo.listar_por_usuario_async(1, FiltroAuditoria(page=1, page_size=10))
        fechas = [reg.creado_iso for reg in regs]
        assert fechas == sorted(fechas, reverse=True)

    async def test_paginacion(self):
        repo = await self._repo()
        pag1 = await repo.listar_por_usuario_async(1, FiltroAuditoria(page=1, page_size=2))
        pag2 = await repo.listar_por_usuario_async(1, FiltroAuditoria(page=2, page_size=2))
        assert len(pag1) == 2
        assert len(pag2) == 1

    async def test_filtro_accion(self):
        repo = await self._repo()
        filtro = FiltroAuditoria(page=1, page_size=10, accion="A")
        regs = await repo.listar_por_usuario_async(1, filtro)
        assert len(regs) == 2
        assert all(reg.accion == "A" for reg in regs)

    async def test_filtro_fechas(self):
        repo = await self._repo()
        filtro = FiltroAuditoria(
            page=1, page_size=10, desde_iso="2026-07-02", hasta_iso="2026-07-03T23:59:59"
        )
        regs = await repo.listar_por_usuario_async(1, filtro)
        assert len(regs) == 2


class TestUseCase:
    async def test_pagina_con_total(self):
        repo = InMemoryAuditoriaRepo()
        for indice in range(5):
            await repo.guardar_async(_reg(1, "A", "2026-07-0" + str(indice + 1)))
        uc = ConsultarMiHistorialUseCase(lector=repo)
        pagina = await uc.ejecutar_async(1, FiltroAuditoria(page=1, page_size=2))
        assert pagina.total == 5
        assert len(pagina.items) == 2
        assert pagina.page == 1


async def _poblar(repo):
    await repo.guardar_async(_reg(1, ACCION_LOGIN_EXITOSO, "2026-07-01T10:00:00.000+00:00"))
    await repo.guardar_async(
        _reg(1, ACCION_PERFIL_CONTACTO_ACTUALIZADO, "2026-07-02T10:00:00.000+00:00")
    )
    await repo.guardar_async(_reg(2, ACCION_LOGIN_EXITOSO, "2026-07-01T10:00:00.000+00:00"))


def _seed_repo():
    repo = InMemoryAuditoriaRepo()
    asyncio.run(_poblar(repo))
    return repo


def _ruta():
    return SL + "api" + SL + "v1" + SL + "me" + SL + "historial"


def _cliente(repo, uid):
    mini = FastAPI()
    mini.include_router(auditoria_router.router, prefix=SL + "api" + SL + "v1" + SL + "me")
    mini.dependency_overrides[require_token] = lambda: {"sub": uid, "roles": ["comisionista"]}
    mini.dependency_overrides[get_consultar_mi_historial_uc] = (
        lambda: ConsultarMiHistorialUseCase(lector=repo)
    )
    return TestClient(mini)


class TestEndpoint:
    def test_solo_ve_lo_suyo(self):
        repo = _seed_repo()
        resp = _cliente(repo, "1").get(_ruta())
        assert resp.status_code == 200
        cuerpo = resp.json()
        assert cuerpo["total"] == 2
        acciones = {item["accion"] for item in cuerpo["items"]}
        assert acciones == {ACCION_LOGIN_EXITOSO, ACCION_PERFIL_CONTACTO_ACTUALIZADO}
        resp2 = _cliente(repo, "2").get(_ruta())
        assert resp2.json()["total"] == 1

    def test_sin_token_401(self):
        mini = FastAPI()
        mini.include_router(auditoria_router.router, prefix=SL + "api" + SL + "v1" + SL + "me")
        resp = TestClient(mini).get(_ruta())
        assert resp.status_code == 401

    def test_sin_rol_autorizado_403(self):
        repo = _seed_repo()
        mini = FastAPI()
        mini.include_router(auditoria_router.router, prefix=SL + "api" + SL + "v1" + SL + "me")
        mini.dependency_overrides[require_token] = lambda: {"sub": "1", "roles": ["autenticado"]}
        mini.dependency_overrides[get_consultar_mi_historial_uc] = (
            lambda: ConsultarMiHistorialUseCase(lector=repo)
        )
        resp = TestClient(mini).get(_ruta())
        assert resp.status_code == 403

    def test_paginacion_http(self):
        repo = _seed_repo()
        resp = _cliente(repo, "1").get(_ruta(), params={"page": 1, "page_size": 1})
        cuerpo = resp.json()
        assert cuerpo["total"] == 2
        assert len(cuerpo["items"]) == 1
        assert cuerpo["page_size"] == 1

    def test_filtro_accion_http(self):
        repo = _seed_repo()
        resp = _cliente(repo, "1").get(_ruta(), params={"accion": ACCION_LOGIN_EXITOSO})
        cuerpo = resp.json()
        assert cuerpo["total"] == 1
        assert cuerpo["items"][0]["accion"] == ACCION_LOGIN_EXITOSO


def test_app_real_registra_historial():
    rutas = [getattr(ruta, "path", "") for ruta in app_real.routes]
    assert any("historial" in ruta for ruta in rutas)
