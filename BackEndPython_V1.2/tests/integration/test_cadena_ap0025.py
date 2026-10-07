from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.main import app as app_real
from src.adapters.api.routers import verificacion_cadena_router
from src.domain.services.calculadora_hash_cadena import CalculadoraHashCadena
from src.domain.services.verificador_cadena import VerificadorCadena
from src.domain.value_objects.eslabon_cadena import EslabonCadena
from src.infrastructure.config.dependencies import get_verificar_cadena_uc, require_token
from src.infrastructure.logging.sellador_log_filter import SelladorLogFilter
from src.infrastructure.security.sellador_cadena_en_memoria import SelladorCadenaEnMemoria

SL = chr(47)


def _sellar_n(sellador, n):
    return [sellador.sellar("evento-" + str(i)) for i in range(n)]


class TestCalculadora:
    def test_hash_determinista(self):
        calc = CalculadoraHashCadena()
        assert calc.hash_contenido("x") == calc.hash_contenido("x")
        assert len(calc.hash_contenido("x")) == 64

    def test_genesis_64_ceros(self):
        assert CalculadoraHashCadena().genesis() == "0" * 64


class TestSellador:
    def test_cadena_secuencial_desde_genesis(self):
        sellador = SelladorCadenaEnMemoria()
        eslabones = _sellar_n(sellador, 3)
        assert [e.secuencia for e in eslabones] == [0, 1, 2]
        assert eslabones[0].hash_previo == CalculadoraHashCadena().genesis()
        assert eslabones[1].hash_previo == eslabones[0].hash_actual
        assert eslabones[2].hash_previo == eslabones[1].hash_actual

    def test_cadena_id_estable(self):
        sellador = SelladorCadenaEnMemoria()
        primero = sellador.cadena_id
        _sellar_n(sellador, 2)
        assert sellador.cadena_id == primero


class TestVerificador:
    def _cadena(self, n=4):
        return _sellar_n(SelladorCadenaEnMemoria(), n)

    def test_cadena_valida(self):
        res = VerificadorCadena().verificar(self._cadena(4))
        assert res.integra is True
        assert res.total == 4
        assert res.primer_roto is None

    def test_cadena_vacia(self):
        res = VerificadorCadena().verificar([])
        assert res.integra is True

    def test_detecta_alteracion(self):
        cadena = self._cadena(4)
        malo = cadena[2]
        cadena[2] = EslabonCadena(malo.secuencia, malo.hash_previo, malo.hash_contenido, "f" * 64)
        res = VerificadorCadena().verificar(cadena)
        assert res.integra is False
        assert res.primer_roto == 2

    def test_detecta_borrado(self):
        cadena = self._cadena(4)
        del cadena[2]
        res = VerificadorCadena().verificar(cadena)
        assert res.integra is False

    def test_detecta_reordenamiento(self):
        cadena = self._cadena(4)
        cadena[1], cadena[2] = cadena[2], cadena[1]
        res = VerificadorCadena().verificar(cadena)
        assert res.integra is False


class TestFiltro:
    def _record(self, name, msg):
        return logging.LogRecord(name, logging.INFO, __file__, 1, msg, None, None)

    def test_sella_eventos_de_seguridad(self):
        sellador = SelladorCadenaEnMemoria()
        filtro = SelladorLogFilter(sellador)
        r1 = self._record("sufi.seguridad.login", "acceso")
        r2 = self._record("sufi.seguridad.password", "cambio")
        assert filtro.filter(r1) is True
        assert filtro.filter(r2) is True
        assert getattr(r1, "sello_secuencia") == 0
        assert getattr(r2, "sello_secuencia") == 1
        cadena = [
            EslabonCadena(
                getattr(r, "sello_secuencia"),
                getattr(r, "sello_hash_previo"),
                getattr(r, "sello_hash_contenido"),
                getattr(r, "sello_hash"),
            )
            for r in (r1, r2)
        ]
        assert VerificadorCadena().verificar(cadena).integra is True

    def test_no_sella_otros_loggers(self):
        filtro = SelladorLogFilter(SelladorCadenaEnMemoria())
        registro = self._record("sqlalchemy.engine", "select 1")
        assert filtro.filter(registro) is True
        assert not hasattr(registro, "sello_secuencia")


class TestEndpoint:
    def _cliente(self):
        mini = FastAPI()
        mini.include_router(
            verificacion_cadena_router.router,
            prefix=SL + "api" + SL + "v1" + SL + "admin" + SL + "logs",
        )
        mini.dependency_overrides[require_token] = lambda: {"sub": "auditor"}
        return TestClient(mini)

    def _payload(self, cadena):
        return {
            "eslabones": [
                {
                    "secuencia": e.secuencia,
                    "hash_previo": e.hash_previo,
                    "hash_contenido": e.hash_contenido,
                    "hash_actual": e.hash_actual,
                }
                for e in cadena
            ]
        }

    def test_verifica_cadena_integra(self):
        cadena = _sellar_n(SelladorCadenaEnMemoria(), 3)
        ruta = SL + "api" + SL + "v1" + SL + "admin" + SL + "logs" + SL + "verificar-cadena"
        resp = self._cliente().post(ruta, json=self._payload(cadena))
        assert resp.status_code == 200
        assert resp.json()["integra"] is True
        assert resp.json()["total"] == 3

    def test_detecta_cadena_rota_por_http(self):
        cadena = _sellar_n(SelladorCadenaEnMemoria(), 3)
        malo = cadena[1]
        cadena[1] = EslabonCadena(
            malo.secuencia, malo.hash_previo, malo.hash_contenido, "a" * 64
        )
        ruta = SL + "api" + SL + "v1" + SL + "admin" + SL + "logs" + SL + "verificar-cadena"
        resp = self._cliente().post(ruta, json=self._payload(cadena))
        assert resp.status_code == 200
        assert resp.json()["integra"] is False
        assert resp.json()["primer_roto"] == 1


def test_app_real_registra_router_cadena():
    rutas = [getattr(ruta, "path", "") for ruta in app_real.routes]
    assert any("verificar-cadena" in ruta for ruta in rutas)


def test_uc_real_disponible():
    uc = get_verificar_cadena_uc()
    cadena = _sellar_n(SelladorCadenaEnMemoria(), 2)
    assert uc.ejecutar(cadena).integra is True
