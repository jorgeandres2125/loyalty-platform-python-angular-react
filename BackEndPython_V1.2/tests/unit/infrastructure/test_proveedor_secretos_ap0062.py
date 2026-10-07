from __future__ import annotations

from collections.abc import Callable

import pytest

from src.domain.exceptions.secreto_no_disponible import SecretoNoDisponible
from src.infrastructure.security.proveedor_secretos_entorno import (
    ProveedorSecretosEntorno,
)
from src.infrastructure.security.proveedor_secretos_pam import ProveedorSecretosPam


class _RelojFalso:
    def __init__(self) -> None:
        self.t: float = 0.0

    def __call__(self) -> float:
        return self.t


def _contador() -> tuple[list[str], Callable[[str], str]]:
    llamadas: list[str] = []

    def recuperador(nombre: str) -> str:
        llamadas.append(nombre)
        return "valor-" + str(len(llamadas))

    return llamadas, recuperador


def test_entorno_devuelve_valor_o_none() -> None:
    proveedor = ProveedorSecretosEntorno({"db_user": "sufi_app", "vacio": ""})
    assert proveedor.obtener("db_user") == "sufi_app"
    assert proveedor.obtener("vacio") is None
    assert proveedor.obtener("inexistente") is None
    proveedor.invalidar("db_user")


def test_pam_cachea_dentro_del_ttl() -> None:
    llamadas, recuperador = _contador()
    reloj = _RelojFalso()
    proveedor = ProveedorSecretosPam(recuperador=recuperador, ttl_seg=100, reloj=reloj)
    assert proveedor.obtener("x") == "valor-1"
    reloj.t = 50.0
    assert proveedor.obtener("x") == "valor-1"
    assert len(llamadas) == 1


def test_pam_refetch_tras_expirar_ttl_rotacion() -> None:
    llamadas, recuperador = _contador()
    reloj = _RelojFalso()
    proveedor = ProveedorSecretosPam(recuperador=recuperador, ttl_seg=100, reloj=reloj)
    proveedor.obtener("x")
    reloj.t = 150.0
    assert proveedor.obtener("x") == "valor-2"
    assert len(llamadas) == 2


def test_pam_invalidar_fuerza_refetch() -> None:
    llamadas, recuperador = _contador()
    proveedor = ProveedorSecretosPam(recuperador=recuperador, ttl_seg=1000, reloj=_RelojFalso())
    proveedor.obtener("x")
    proveedor.invalidar("x")
    proveedor.obtener("x")
    assert len(llamadas) == 2


def test_pam_fail_secure_si_el_broker_falla() -> None:
    def recuperador(nombre: str) -> str:
        raise RuntimeError("broker caido")

    proveedor = ProveedorSecretosPam(recuperador=recuperador, ttl_seg=100, reloj=_RelojFalso())
    with pytest.raises(SecretoNoDisponible):
        proveedor.obtener("x")
