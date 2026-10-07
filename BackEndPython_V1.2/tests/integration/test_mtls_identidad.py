from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.adapters.api.main import app as app_real
from src.adapters.api.middleware.mtls_identidad_middleware import MtlsIdentidadMiddleware
from src.domain.value_objects.identidad_certificado import IdentidadCertificado
from src.domain.value_objects.principal_certificado import PrincipalCertificado
from src.infrastructure.security.registro_certificados_estatico import (
    RegistroCertificadosEstatico,
)
from src.shared.constants.mtls import (
    HEADER_CLIENT_CERT_FINGERPRINT,
    HEADER_MTLS_EDGE_SECRET,
    RUTAS_MTLS_OBLIGATORIO,
)

SL = chr(47)
_FINGERPRINT = "AA:BB:CC:11:22:33"
_SECRETO = "edge-shared-secret"


class TestIdentidadCertificado:
    def test_normaliza_fingerprint(self) -> None:
        ident = IdentidadCertificado(fingerprint="AA:BB:cc", subject=" CN=x ", serial=" 01 ")
        assert ident.fingerprint == "aabbcc"
        assert ident.subject == "CN=x"
        assert ident.serial == "01"

    def test_rechaza_fingerprint_vacio(self) -> None:
        with pytest.raises(ValueError):
            IdentidadCertificado(fingerprint="  ", subject="", serial="")


class TestPrincipalCertificado:
    def test_exige_sistema(self) -> None:
        with pytest.raises(ValueError):
            PrincipalCertificado(sistema="  ", empresa="acme")

    def test_strip(self) -> None:
        principal = PrincipalCertificado(sistema=" sapin ", empresa=" msp ")
        assert principal.sistema == "sapin"
        assert principal.empresa == "msp"


class TestRegistroCertificadosEstatico:
    def test_desde_config_resuelve(self) -> None:
        registro = RegistroCertificadosEstatico.desde_config(
            "AA:BB:CC:11:22:33|sapin|msp;DD:EE|ingesta|sufi"
        )
        principal = registro.resolver(
            IdentidadCertificado(fingerprint=_FINGERPRINT, subject="", serial="")
        )
        assert principal is not None
        assert principal.sistema == "sapin"
        assert principal.empresa == "msp"

    def test_desconocido_da_none(self) -> None:
        registro = RegistroCertificadosEstatico.desde_config("AA|sapin|msp")
        ident = IdentidadCertificado(fingerprint="ZZ", subject="", serial="")
        assert registro.resolver(ident) is None

    def test_entrada_malformada_se_ignora(self) -> None:
        registro = RegistroCertificadosEstatico.desde_config("malo;CC|s2|e2")
        valido = IdentidadCertificado(fingerprint="CC", subject="", serial="")
        malo = IdentidadCertificado(fingerprint="malo", subject="", serial="")
        assert registro.resolver(valido) is not None
        assert registro.resolver(malo) is None


def _mini_app(enabled: bool) -> FastAPI:
    mini = FastAPI()
    registro = RegistroCertificadosEstatico.desde_config(_FINGERPRINT + "|sapin|msp")
    mini.add_middleware(
        MtlsIdentidadMiddleware,
        registro=registro,
        rutas_obligatorias=RUTAS_MTLS_OBLIGATORIO,
        edge_secret=_SECRETO,
        enabled=enabled,
    )

    @mini.get(RUTAS_MTLS_OBLIGATORIO[0] + SL + "ping")
    def protegido(request: Request) -> dict[str, str | None]:
        principal = getattr(request.state, "principal_certificado", None)
        return {"sistema": principal.sistema if principal is not None else None}

    @mini.get(SL + "publico" + SL + "ping")
    def publico() -> dict[str, bool]:
        return {"ok": True}

    return mini


_CLIENTE = TestClient(_mini_app(True))
_CLIENTE_OFF = TestClient(_mini_app(False))
_RUTA = RUTAS_MTLS_OBLIGATORIO[0] + SL + "ping"
_PUB = SL + "publico" + SL + "ping"


class TestMtlsMiddleware:
    def test_ruta_critica_sin_cert_da_403(self) -> None:
        assert _CLIENTE.get(_RUTA).status_code == 403

    def test_ruta_critica_con_cert_valido_da_200(self) -> None:
        resp = _CLIENTE.get(
            _RUTA,
            headers={
                HEADER_CLIENT_CERT_FINGERPRINT: _FINGERPRINT,
                HEADER_MTLS_EDGE_SECRET: _SECRETO,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["sistema"] == "sapin"

    def test_cert_con_secreto_edge_invalido_da_403(self) -> None:
        resp = _CLIENTE.get(
            _RUTA,
            headers={
                HEADER_CLIENT_CERT_FINGERPRINT: _FINGERPRINT,
                HEADER_MTLS_EDGE_SECRET: "malo",
            },
        )
        assert resp.status_code == 403

    def test_cert_desconocido_da_403(self) -> None:
        resp = _CLIENTE.get(
            _RUTA,
            headers={
                HEADER_CLIENT_CERT_FINGERPRINT: "99:99:99",
                HEADER_MTLS_EDGE_SECRET: _SECRETO,
            },
        )
        assert resp.status_code == 403

    def test_ruta_publica_sin_cert_da_200(self) -> None:
        assert _CLIENTE.get(_PUB).status_code == 200

    def test_deshabilitado_no_bloquea(self) -> None:
        assert _CLIENTE_OFF.get(_RUTA).status_code == 200


def test_app_real_registra_mtls_middleware() -> None:
    clases = [getattr(m.cls, "__name__", "") for m in app_real.user_middleware]
    assert MtlsIdentidadMiddleware.__name__ in clases
