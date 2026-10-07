from __future__ import annotations

import pytest

from src.application.services.resolvedor_credencial_bd import ResolvedorCredencialBd
from src.domain.exceptions.secreto_no_disponible import SecretoNoDisponible


class _FakeProveedor:
    def __init__(self, valores: dict[str, str]) -> None:
        self._valores: dict[str, str] = dict(valores)
        self.invalidados: list[str] = []

    def obtener(self, nombre: str) -> str | None:
        return self._valores.get(nombre) or None

    def invalidar(self, nombre: str) -> None:
        self.invalidados.append(nombre)


def _resolver(
    modo: str, valores: dict[str, str] | None = None, url_directa: str = "url-directa"
) -> tuple[ResolvedorCredencialBd, _FakeProveedor]:
    prov = _FakeProveedor(valores or {})
    resolver = ResolvedorCredencialBd(
        modo=modo,
        url_directa=url_directa,
        proveedor=prov,
        host="127.0.0.1",
        port=1433,
        database="sufi_db",
        driver="ODBC Driver 17 for SQL Server",
        nombre_usuario="db_user",
        nombre_password="db_password",
    )
    return resolver, prov


def test_modo_env_devuelve_url_directa_sin_tocar_proveedor() -> None:
    resolver, prov = _resolver("env", url_directa="url-estatica-actual")
    assert resolver.url() == "url-estatica-actual"
    assert prov.invalidados == []


def test_modo_pam_construye_url_con_credencial_del_broker() -> None:
    resolver, _ = _resolver("pam", {"db_user": "sufi_app", "db_password": "Secreta123!"})
    url: str = resolver.url()
    assert url.startswith("mssql+aioodbc")
    assert "sufi_app" in url
    assert "sufi_db" in url


def test_modo_pam_sin_credencial_falla_seguro() -> None:
    resolver, _ = _resolver("pam", {"db_user": "sufi_app"})
    with pytest.raises(SecretoNoDisponible):
        resolver.url()


def test_invalidar_propaga_al_proveedor() -> None:
    resolver, prov = _resolver("pam", {"db_user": "u", "db_password": "p"})
    resolver.invalidar()
    assert "db_user" in prov.invalidados
    assert "db_password" in prov.invalidados
