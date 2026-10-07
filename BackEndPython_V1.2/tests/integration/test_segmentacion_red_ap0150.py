"""AP-0150: pruebas del gate de segmentacion de red (validar_segmentacion.py).

Verifican que el inventario y las NetworkPolicies reales cumplen las invariantes, y que el gate
RECHAZA cada forma de topologia plana (BD alcanzable fuera de la capa app, componente critico
expuesto a Internet, falta de WAF en el borde, o NetworkPolicy sin deny-by-default).
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from typing import Any

import yaml

_REPO: Path = Path(__file__).resolve().parents[2]
_NET_DIR: Path = _REPO / "deploy" / "network"
_INV: Path = _NET_DIR / "inventario-segmentacion.yaml"
_NETPOL: Path = _NET_DIR / "networkpolicies.yaml"


def _cargar_modulo() -> Any:
    ruta: Path = _NET_DIR / "validar_segmentacion.py"
    spec = importlib.util.spec_from_file_location("validar_segmentacion", ruta)
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _inventario() -> dict[str, Any]:
    return yaml.safe_load(_INV.read_text(encoding="utf-8"))


def _netpolicies() -> list[dict[str, Any]]:
    return list(yaml.safe_load_all(_NETPOL.read_text(encoding="utf-8")))


def test_topologia_real_es_valida() -> None:
    modulo = _cargar_modulo()
    errores: list[str] = modulo.validar(_INV, _NETPOL)
    assert errores == [], errores


def test_web_a_datos_es_rechazado() -> None:
    modulo = _cargar_modulo()
    inv: dict[str, Any] = copy.deepcopy(_inventario())
    inv["flujos_permitidos"].append(
        {"origen": "web", "destino": "data", "puertos": [1433]}
    )
    errores: list[str] = []
    modulo._validar_inventario(inv, errores)
    assert any("data" in e and "web" in e for e in errores)


def test_internet_a_app_es_rechazado() -> None:
    modulo = _cargar_modulo()
    inv: dict[str, Any] = copy.deepcopy(_inventario())
    inv["flujos_permitidos"].append(
        {"origen": "internet", "destino": "app", "puertos": [443]}
    )
    errores: list[str] = []
    modulo._validar_inventario(inv, errores)
    assert any("Internet" in e for e in errores)


def test_falta_waf_en_el_borde_es_rechazado() -> None:
    modulo = _cargar_modulo()
    inv: dict[str, Any] = copy.deepcopy(_inventario())
    for zona in inv["zonas"]:
        if zona["id"] == "dmz":
            zona["controles"] = []
    errores: list[str] = []
    modulo._validar_inventario(inv, errores)
    assert any("WAF" in e for e in errores)


def test_netpol_sin_deny_default_en_datos_es_rechazado() -> None:
    modulo = _cargar_modulo()
    docs: list[dict[str, Any]] = copy.deepcopy(_netpolicies())
    filtrado: list[dict[str, Any]] = [
        d
        for d in docs
        if not (
            isinstance(d, dict)
            and d.get("metadata", {}).get("name") == "default-deny-ingress-data"
        )
    ]
    errores: list[str] = []
    modulo._validar_networkpolicies(filtrado, errores)
    assert any("deny-by-default" in e and "sufi-data" in e for e in errores)


def test_netpol_datos_desde_otra_zona_es_rechazado() -> None:
    modulo = _cargar_modulo()
    docs: list[dict[str, Any]] = copy.deepcopy(_netpolicies())
    for d in docs:
        if isinstance(d, dict) and d.get("metadata", {}).get("name") == "permitir-solo-app-a-datos":
            d["spec"]["ingress"][0]["from"][0]["namespaceSelector"]["matchLabels"]["zona"] = "web"
    errores: list[str] = []
    modulo._validar_networkpolicies(docs, errores)
    assert any("distinta de app" in e for e in errores)
