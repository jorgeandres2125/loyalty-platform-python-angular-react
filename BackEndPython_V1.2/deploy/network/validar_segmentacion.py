#!/usr/bin/env python3
"""AP-0150: gate de segmentacion de red (anti-topologia-plana).

Valida, contra el inventario canonico (inventario-segmentacion.yaml) y las NetworkPolicies
de Kubernetes (networkpolicies.yaml), un conjunto de invariantes de seguridad de red. Si
alguno se incumple, el build FALLA: impide fusionar una topologia en la que la base de datos
sea alcanzable fuera de la capa de aplicacion, un componente critico quede expuesto a Internet,
o falte el WAF sobre el ingreso publico.

Es la herramienta auditable del lado del proyecto para AP-0150. No despliega infraestructura;
verifica que la segmentacion declarada como codigo cumple las invariantes antes de que
Infraestructura la materialice.

Uso: validar_segmentacion.py [--inventario <yaml>] [--networkpolicies <yaml>]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

_AQUI: Path = Path(__file__).resolve()
_INV_DEFECTO: Path = _AQUI.parent / "inventario-segmentacion.yaml"
_NETPOL_DEFECTO: Path = _AQUI.parent / "networkpolicies.yaml"

_PUERTO_DATOS: int = 1433
_ORIGENES_DATOS_PERMITIDOS: frozenset[str] = frozenset({"app", "mgmt"})
_NS_APP: str = "sufi-app"
_NS_DATA: str = "sufi-data"


def _clave_flujo(flujo: dict[str, Any]) -> tuple[str, str]:
    return (str(flujo["origen"]), str(flujo["destino"]))


def _validar_inventario(datos: dict[str, Any], errores: list[str]) -> None:
    zonas: dict[str, dict[str, Any]] = {z["id"]: z for z in datos.get("zonas", [])}
    permitidos: list[dict[str, Any]] = datos.get("flujos_permitidos", [])
    prohibidos: list[dict[str, Any]] = datos.get("flujos_prohibidos", [])

    # 1. Toda zona referenciada en un flujo debe existir.
    for flujo in permitidos:
        for extremo in ("origen", "destino"):
            zona_ref: str = flujo[extremo]
            if zona_ref not in zonas:
                errores.append(f"Flujo permitido referencia zona inexistente: {zona_ref!r}.")

    # 2. Ningun flujo prohibido puede aparecer entre los permitidos.
    permitidos_set: set[tuple[str, str]] = {_clave_flujo(f) for f in permitidos}
    for prohibido in prohibidos:
        clave: tuple[str, str] = _clave_flujo(prohibido)
        if clave in permitidos_set:
            motivo: str = prohibido.get("motivo", "")
            errores.append(
                f"Flujo prohibido {clave[0]} -> {clave[1]} aparece como PERMITIDO: {motivo}"
            )

    # 3. Ninguna zona critica recibe trafico directo desde Internet.
    for flujo in permitidos:
        destino_id: str = flujo["destino"]
        destino: dict[str, Any] = zonas.get(destino_id, {})
        if flujo["origen"] == "internet" and destino.get("critica", False):
            errores.append(
                f"Zona critica {destino_id!r} expuesta directo a Internet "
                f"(debe pasar por la DMZ/WAF)."
            )

    # 4. La capa de datos solo la alcanzan origenes autorizados; el 1433 solo desde app/mgmt.
    autorizados: list[str] = sorted(_ORIGENES_DATOS_PERMITIDOS)
    for flujo in permitidos:
        if flujo["destino"] != "data":
            continue
        origen_id: str = flujo["origen"]
        if origen_id not in _ORIGENES_DATOS_PERMITIDOS:
            errores.append(
                f"La capa de datos es alcanzable desde {origen_id!r}; permitidos: {autorizados}."
            )
        puertos: list[int] = flujo.get("puertos", [])
        if _PUERTO_DATOS in puertos and origen_id not in _ORIGENES_DATOS_PERMITIDOS:
            errores.append(
                f"Puerto {_PUERTO_DATOS} de la BD abierto a {origen_id!r} (no autorizado)."
            )

    # 5. El ingreso publico solo entra por una zona con WAF (deny-by-default en el borde).
    for flujo in permitidos:
        if flujo["origen"] != "internet":
            continue
        destino_id = flujo["destino"]
        destino = zonas.get(destino_id, {})
        if "waf" not in destino.get("controles", []):
            errores.append(
                f"El ingreso desde Internet a {destino_id!r} no pasa por una zona con WAF."
            )

    # 6. Los controles requeridos deben estar declarados.
    ids_control: set[str] = {c["id"] for c in datos.get("controles", [])}
    for requerido in ("waf", "acl_datos", "ids", "ips"):
        if requerido not in ids_control:
            errores.append(f"Control requerido ausente del inventario: {requerido!r}.")


def _validar_networkpolicies(docs: list[dict[str, Any]], errores: list[str]) -> None:
    politicas: list[dict[str, Any]] = [
        d for d in docs if isinstance(d, dict) and d.get("kind") == "NetworkPolicy"
    ]
    if not politicas:
        errores.append("networkpolicies.yaml no contiene ninguna NetworkPolicy.")
        return

    def _en_ns(ns: str) -> list[dict[str, Any]]:
        return [p for p in politicas if p.get("metadata", {}).get("namespace") == ns]

    # a. Debe existir un deny-by-default (selector vacio, sin reglas de ingreso) en app y datos.
    for ns in (_NS_APP, _NS_DATA):
        del_ns: list[dict[str, Any]] = _en_ns(ns)
        if not del_ns:
            errores.append(f"No hay NetworkPolicy en el namespace {ns!r}.")
            continue
        tiene_deny: bool = any(
            p.get("spec", {}).get("podSelector") == {}
            and "Ingress" in p.get("spec", {}).get("policyTypes", [])
            and not p.get("spec", {}).get("ingress")
            for p in del_ns
        )
        if not tiene_deny:
            errores.append(f"Falta un deny-by-default de ingreso en el namespace {ns!r}.")

    # b. En el namespace de datos, todo ingreso permitido viene SOLO de la capa app y por 1433.
    for p in _en_ns(_NS_DATA):
        nombre_pol: str = p.get("metadata", {}).get("name", "?")
        for regla in p.get("spec", {}).get("ingress", []) or []:
            for origen in regla.get("from", []) or []:
                etiquetas: dict[str, Any] = origen.get("namespaceSelector", {}).get(
                    "matchLabels", {}
                )
                if etiquetas.get("zona") != "app":
                    errores.append(
                        f"NetworkPolicy {nombre_pol!r}: la capa de datos acepta ingreso de una "
                        f"zona distinta de app ({etiquetas!r})."
                    )
            for puerto in regla.get("ports", []) or []:
                valor_puerto: Any = puerto.get("port")
                if valor_puerto != _PUERTO_DATOS:
                    errores.append(
                        f"NetworkPolicy {nombre_pol!r}: la capa de datos abre un puerto distinto "
                        f"de {_PUERTO_DATOS} ({valor_puerto!r})."
                    )


def validar(inventario_path: Path, netpol_path: Path) -> list[str]:
    errores: list[str] = []
    datos: dict[str, Any] = yaml.safe_load(inventario_path.read_text(encoding="utf-8"))
    _validar_inventario(datos, errores)
    docs: list[dict[str, Any]] = list(yaml.safe_load_all(netpol_path.read_text(encoding="utf-8")))
    _validar_networkpolicies(docs, errores)
    return errores


def main() -> int:
    parser = argparse.ArgumentParser(description="AP-0150 gate de segmentacion de red")
    parser.add_argument("--inventario", default=str(_INV_DEFECTO))
    parser.add_argument("--networkpolicies", default=str(_NETPOL_DEFECTO))
    args = parser.parse_args()

    errores: list[str] = validar(Path(args.inventario), Path(args.networkpolicies))
    if errores:
        print("AP-0150: FALLO la validacion de segmentacion de red:", file=sys.stderr)
        for err in errores:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("AP-0150 OK: segmentacion valida (deny-by-default, BD solo desde app, WAF en el borde).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
