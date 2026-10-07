from __future__ import annotations

import pytest

from src.domain.exceptions.secreto_no_disponible import SecretoNoDisponible
from src.infrastructure.security.cliente_pam_http import ClientePamHttp


class _FakeHttp:
    def __init__(self, respuesta: dict[str, object]) -> None:
        self._respuesta: dict[str, object] = respuesta
        self.ultima_url: str = ""
        self.ultima_consulta: dict[str, str] = {}

    def __call__(self, url: str, consulta: dict[str, str]) -> dict[str, object]:
        self.ultima_url = url
        self.ultima_consulta = consulta
        return self._respuesta


def test_estilo_cyberark_ccp_extrae_content() -> None:
    http = _FakeHttp({"Content": "S3cret-app!", "UserName": "sufi_app"})
    cliente = ClientePamHttp(
        base_url="https-broker-ccp",
        app_id="SUFI_APP",
        safe="SUFI_DB",
        campo_secreto="Content",
        http_get=http,
    )
    assert cliente.recuperar("db_password") == "S3cret-app!"
    assert http.ultima_consulta["Object"] == "db_password"
    assert http.ultima_consulta["AppID"] == "SUFI_APP"
    assert http.ultima_consulta["Safe"] == "SUFI_DB"


def test_estilo_vault_extrae_por_ruta_con_puntos() -> None:
    http = _FakeHttp({"data": {"data": {"password": "V4ult-secret"}}})
    cliente = ClientePamHttp(
        base_url="broker-vault",
        app_id="",
        safe="",
        campo_secreto="data.data.password",
        http_get=http,
    )
    assert cliente.recuperar("db_password") == "V4ult-secret"
    # app_id y safe vacios se omiten de la consulta
    assert "AppID" not in http.ultima_consulta
    assert "Safe" not in http.ultima_consulta


def test_campo_ausente_falla_seguro() -> None:
    http = _FakeHttp({"otra_cosa": "x"})
    cliente = ClientePamHttp(
        base_url="broker",
        app_id="A",
        safe="S",
        campo_secreto="Content",
        http_get=http,
    )
    with pytest.raises(SecretoNoDisponible):
        cliente.recuperar("db_password")


def test_error_del_broker_se_propaga() -> None:
    def http_get(url: str, consulta: dict[str, str]) -> dict[str, object]:
        raise RuntimeError("broker 500")

    cliente = ClientePamHttp(
        base_url="broker",
        app_id="A",
        safe="S",
        campo_secreto="Content",
        http_get=http_get,
    )
    with pytest.raises(RuntimeError):
        cliente.recuperar("db_password")
