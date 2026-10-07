from __future__ import annotations

import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.main import app as app_real
from src.adapters.api.routers import retencion_router
from src.application.use_cases.obtener_politica_retencion_use_case import (
    ObtenerPoliticaRetencionUseCase,
)
from src.domain.services.clasificador_retencion import ClasificadorRetencion
from src.domain.value_objects.retencion_categoria import RetencionCategoria
from src.infrastructure.config.dependencies import get_politica_retencion_uc, require_token
from src.infrastructure.config.settings import Settings
from src.infrastructure.logging.retencion_log_filter import RetencionLogFilter

SL = chr(47)


def _dias():
    return {
        RetencionCategoria.SEGURIDAD: 2555,
        RetencionCategoria.AUDITORIA: 2555,
        RetencionCategoria.ADMINISTRACION: 2555,
        RetencionCategoria.OPERACION: 730,
        RetencionCategoria.ERROR: 365,
    }


class TestClasificador:
    def _clf(self):
        return ClasificadorRetencion(_dias())

    def test_seguridad(self):
        res = self._clf().clasificar("sufi.seguridad.login", "INFO")
        assert res.categoria == RetencionCategoria.SEGURIDAD
        assert res.dias == 2555

    def test_admin(self):
        res = self._clf().clasificar("sufi.admin.usuarios", "INFO")
        assert res.categoria == RetencionCategoria.ADMINISTRACION

    def test_auditoria(self):
        res = self._clf().clasificar("sufi.auditoria.datos", "INFO")
        assert res.categoria == RetencionCategoria.AUDITORIA

    def test_error_por_nivel(self):
        res = self._clf().clasificar("sqlalchemy.engine", "ERROR")
        assert res.categoria == RetencionCategoria.ERROR
        assert res.dias == 365

    def test_operacion_por_defecto(self):
        res = self._clf().clasificar("uvicorn.access", "INFO")
        assert res.categoria == RetencionCategoria.OPERACION
        assert res.dias == 730

    def test_seguridad_prevalece_sobre_error(self):
        res = self._clf().clasificar("sufi.seguridad.login", "ERROR")
        assert res.categoria == RetencionCategoria.SEGURIDAD


class TestFiltro:
    def _record(self, name, nivel):
        return logging.LogRecord(name, nivel, __file__, 1, "evento", None, None)

    def test_adjunta_categoria_y_dias(self):
        filtro = RetencionLogFilter(ClasificadorRetencion(_dias()))
        rec = self._record("sufi.seguridad.login", logging.INFO)
        assert filtro.filter(rec) is True
        assert getattr(rec, "retencion_categoria") == "seguridad"
        assert getattr(rec, "retencion_dias") == 2555

    def test_operacion_para_otros(self):
        filtro = RetencionLogFilter(ClasificadorRetencion(_dias()))
        rec = self._record("uvicorn.access", logging.INFO)
        assert filtro.filter(rec) is True
        assert getattr(rec, "retencion_categoria") == "operacion"


class TestSettings:
    def test_mapa_cinco_categorias(self):
        mapa = Settings().retencion_dias_por_categoria()
        assert len(mapa) == 5
        assert mapa[RetencionCategoria.SEGURIDAD] >= 90

    def test_rechaza_por_debajo_del_minimo(self):
        with pytest.raises(ValueError):
            Settings(retencion_error_dias=10)


class TestUseCase:
    def test_politica_cinco_items_con_base(self):
        uc = ObtenerPoliticaRetencionUseCase(ClasificadorRetencion(_dias()))
        items = uc.ejecutar()
        assert len(items) == 5
        seg = [it for it in items if it.categoria == RetencionCategoria.SEGURIDAD][0]
        assert seg.dias == 2555
        assert seg.base_regulatoria != ""


class TestEndpoint:
    def _cliente(self):
        mini = FastAPI()
        mini.include_router(
            retencion_router.router,
            prefix=SL + "api" + SL + "v1" + SL + "admin" + SL + "logs",
        )
        mini.dependency_overrides[require_token] = lambda: {"sub": "auditor"}
        return TestClient(mini)

    def test_consulta_politica(self):
        ruta = SL + "api" + SL + "v1" + SL + "admin" + SL + "logs" + SL + "politica-retencion"
        resp = self._cliente().get(ruta)
        assert resp.status_code == 200
        cuerpo = resp.json()
        assert cuerpo["total"] == 5
        categorias = [it["categoria"] for it in cuerpo["items"]]
        assert "seguridad" in categorias


def test_app_real_registra_router_retencion():
    rutas = [getattr(ruta, "path", "") for ruta in app_real.routes]
    assert any("politica-retencion" in ruta for ruta in rutas)


def test_uc_real_disponible():
    uc = get_politica_retencion_uc()
    assert len(uc.ejecutar()) == 5
