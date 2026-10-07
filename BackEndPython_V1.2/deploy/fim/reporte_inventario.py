#!/usr/bin/env python3
"""AP-0121: genera el reporte de inventario clasificado de archivos criticos a partir del
registro canonico (critical-files.yaml). Produce inventario-archivos-criticos.md: una tabla por
sistema con criticidad, responsable, frecuencia de revision y numero de archivos. Es la evidencia
de auditoria de la definicion formal (Fase 2). Requiere PyYAML.

Uso: reporte_inventario.py [--registry <yaml>] [--root <repo>] [--out <md>]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

_SALTO = chr(10)
_AQUI = Path(__file__).resolve()
_REPO_DEFECTO = _AQUI.parents[3]
_REGISTRO_DEFECTO = _AQUI.parent / "critical-files.yaml"
_SALIDA_DEFECTO = _AQUI.parent / "inventario-archivos-criticos.md"


def _contar(base: Path, patrones: list[str], excluidos: set[str]) -> int:
    total = 0
    for patron in patrones:
        for ruta in base.glob(patron):
            if ruta.is_file() and not any(p in excluidos for p in ruta.parts):
                total += 1
    return total


def construir(registro_path: Path, repo_root: Path) -> str:
    datos = yaml.safe_load(registro_path.read_text(encoding="utf-8"))
    excluidos: set[str] = set(datos.get("exclude_dirs", []))
    filas: list[str] = []
    gran_total = 0
    for nombre, sistema in datos.get("systems", {}).items():
        base = repo_root / sistema["base"]
        n = _contar(base, sistema.get("patterns", []), excluidos)
        gran_total += n
        filas.append(
            "| {sis} | {crit} | {resp} | {rev} | {base} | {n} |".format(
                sis=nombre,
                crit=sistema.get("criticidad", "-"),
                resp=sistema.get("responsable", "-"),
                rev=sistema.get("revision", "-"),
                base=sistema["base"],
                n=n,
            )
        )
    lineas: list[str] = [
        "# Inventario Clasificado de Archivos Criticos (AP-0121)",
        "",
        "Generado automaticamente desde `critical-files.yaml`. No editar a mano.",
        "",
        "| Sistema | Criticidad | Responsable | Revision | Base | Archivos |",
        "|---|---|---|---|---|---|",
    ]
    lineas.extend(filas)
    lineas.append("| **TOTAL** | | | | | **{}** |".format(gran_total))
    lineas.append("")
    lineas.append("Criticidad: C1 critico, C2 alto, C3 medio. Fuente: critical-files.yaml (Git).")
    lineas.append("")
    return _SALTO.join(lineas)


def main() -> int:
    parser = argparse.ArgumentParser(description="AP-0121 reporte de inventario clasificado")
    parser.add_argument("--registry", default=str(_REGISTRO_DEFECTO))
    parser.add_argument("--root", default=str(_REPO_DEFECTO))
    parser.add_argument("--out", default=str(_SALIDA_DEFECTO))
    args = parser.parse_args()
    contenido = construir(Path(args.registry), Path(args.root))
    Path(args.out).write_text(contenido, encoding="utf-8")
    print(f"AP-0121: reporte de inventario -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())