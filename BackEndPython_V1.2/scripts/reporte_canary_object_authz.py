"""AP-0055 -- Reporte de readiness del canary de autorizacion a nivel de objeto.

Solo lectura. Consulta el historial de auditoria (audit_log, AP-0028) buscando las
decisiones de acceso a objeto registradas en modo "audit" (el canary de staging, donde
OBJECT_AUTHZ_MODE=audit no bloquea pero registra lo que enforce SI bloquearia) y emite un
veredicto de promocion:

  LISTO       -- hubo trafico observado y CERO denegaciones potenciales, seguro promover
                 staging a enforce (produccion ya esta en enforce).
  REVISAR     -- hubo denegaciones potenciales: se listan agrupadas para que una persona
                 confirme que cada una es un intento legitimo de acceso cruzado (BOLA-IDOR,
                 seguro de bloquear) y no un usuario valido mal denegado (arreglar politica
                 antes de promover).
  INSUFICIENTE-- no se observo trafico de acceso a objeto en la ventana: no hay evidencia,
                 NO promover todavia (dejar soakear el canary con trafico real de QA-UAT).

Uso (desde el directorio del backend):
    python scripts/reporte_canary_object_authz.py --dias 7

Respeta APP_ENV: apunta a la base de datos del entorno activo (en staging, la del canary).
Codigos de salida: 0=LISTO, 2=REVISAR, 3=INSUFICIENTE, 4=error de conexion.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.infrastructure.config.settings import Settings

ACCION_OBJETO: str = "acceso_objeto"
MODO_AUDIT: str = "audit"
SEP_EQ: str = "=" * 72
SEP_LN: str = "-" * 72


async def _consultar(database_url: str, desde_iso: str) -> list[dict[str, object]]:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    filas: list[dict[str, object]] = []
    try:
        async with engine.connect() as conn:
            resultado = await conn.execute(
                text(
                    "SELECT user_id, entidad, entidad_id, detalle, creado_iso "
                    "FROM audit_log "
                    "WHERE accion = :accion AND creado_iso >= :desde "
                    "ORDER BY creado_iso"
                ),
                {"accion": ACCION_OBJETO, "desde": desde_iso},
            )
            for user_id, entidad, entidad_id, detalle, creado_iso in resultado:
                filas.append(
                    {
                        "user_id": user_id,
                        "entidad": entidad,
                        "entidad_id": entidad_id,
                        "detalle": detalle,
                        "creado_iso": creado_iso,
                    }
                )
    finally:
        await engine.dispose()
    return filas


def _clasificar(filas: list[dict[str, object]]) -> tuple[int, list[dict[str, object]]]:
    observadas_audit: int = 0
    denegaciones: list[dict[str, object]] = []
    for fila in filas:
        crudo = fila.get("detalle")
        if not crudo:
            continue
        try:
            info = json.loads(str(crudo))
        except (TypeError, ValueError):
            continue
        if info.get("modo") != MODO_AUDIT:
            continue
        observadas_audit += 1
        if info.get("permitido") is False:
            denegaciones.append(
                {
                    "user_id": fila.get("user_id"),
                    "entidad": fila.get("entidad"),
                    "entidad_id": fila.get("entidad_id"),
                    "accion": info.get("accion"),
                    "motivo": info.get("motivo"),
                    "creado_iso": fila.get("creado_iso"),
                }
            )
    return observadas_audit, denegaciones


def _imprimir_reporte(
    dias: int,
    entorno: str,
    observadas: int,
    denegaciones: list[dict[str, object]],
) -> int:
    print(SEP_EQ)
    print("AP-0055 -- Readiness del canary de autorizacion a nivel de objeto")
    print(SEP_EQ)
    print(f"Entorno (APP_ENV)        : {entorno}")
    print(f"Ventana de observacion   : ultimos {dias} dias")
    print(f"Decisiones observadas    : {observadas} (modo audit)")
    print(f"Denegaciones potenciales : {len(denegaciones)}")
    print(SEP_LN)

    if observadas == 0:
        print("VEREDICTO: INSUFICIENTE")
        print("  No hay decisiones de acceso a objeto en modo audit en la ventana.")
        print("  No promover: dejar el canary soakear con trafico real de QA-UAT.")
        return 3

    if not denegaciones:
        print("VEREDICTO: LISTO")
        print("  Hubo trafico observado y CERO denegaciones potenciales.")
        print("  Seguro promover staging a enforce (produccion ya esta en enforce).")
        return 0

    print("VEREDICTO: REVISAR")
    print("  Hubo denegaciones que enforce habria bloqueado. Confirmar que cada una")
    print("  es un acceso cruzado ilegitimo (BOLA-IDOR) y no un usuario mal denegado.")
    print(SEP_LN)
    resumen: Counter[str] = Counter()
    for d in denegaciones:
        clave = f"{d['entidad']} :: {d['accion']} :: {d['motivo']}"
        resumen[clave] += 1
    print("  Agrupado (entidad :: accion :: motivo -> cantidad):")
    for clave, n in resumen.most_common():
        print(f"    [{n:>4}] {clave}")
    print(SEP_LN)
    print("  Detalle (hasta 50 eventos):")
    for d in denegaciones[:50]:
        print(
            f"    uid={d['user_id']} entidad={d['entidad']} id={d['entidad_id']} "
            f"accion={d['accion']} motivo={d['motivo']} ts={d['creado_iso']}"
        )
    if len(denegaciones) > 50:
        print(f"    ... y {len(denegaciones) - 50} mas")
    return 2


async def _main_async(dias: int) -> int:
    ajustes = Settings()
    desde = datetime.now(UTC) - timedelta(days=dias)
    desde_iso = desde.isoformat(timespec="milliseconds")
    try:
        filas = await _consultar(ajustes.database_url, desde_iso)
    except Exception as exc:  # noqa: BLE001 -- script operativo, reporta y sale
        print(f"ERROR: no se pudo consultar la base de datos: {exc}", file=sys.stderr)
        return 4
    observadas, denegaciones = _clasificar(filas)
    return _imprimir_reporte(dias, ajustes.app_env, observadas, denegaciones)


def main() -> None:
    parser = argparse.ArgumentParser(description="AP-0055 readiness del canary de object-authz")
    parser.add_argument("--dias", type=int, default=7, help="ventana de observacion en dias")
    args = parser.parse_args()
    codigo = asyncio.run(_main_async(args.dias))
    sys.exit(codigo)


if __name__ == "__main__":
    main()
