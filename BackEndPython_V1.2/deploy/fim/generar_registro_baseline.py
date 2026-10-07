#!/usr/bin/env python3
"""AP-0121: genera la linea base (baseline) de integridad a partir del REGISTRO canonico de
archivos criticos (critical-files.yaml). Recorre, por sistema, los patrones definidos desde la
raiz del repositorio, calcula el hash SHA-256 de cada archivo y escribe fim-baseline.json:
{ruta_relativa_al_repo: "sha256:..."}.

Lo consume el gate de CI (fim.yml): si el baseline recien generado difiere del versionado, hay
un cambio no revisado en un archivo critico y el build falla. Requiere PyYAML.

Uso: generar_registro_baseline.py [--registry <yaml>] [--root <repo>] [--out <json>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml

_TAMANO_BLOQUE = 65536
_SALTO = chr(10)
_AQUI = Path(__file__).resolve()
_REPO_DEFECTO = _AQUI.parents[3]
_REGISTRO_DEFECTO = _AQUI.parent / "critical-files.yaml"
_SALIDA_DEFECTO = _AQUI.parent / "fim-baseline.json"


def _hash_archivo(ruta: Path) -> str:
    hasher = hashlib.sha256()
    with open(ruta, "rb") as fh:
        for bloque in iter(lambda: fh.read(_TAMANO_BLOQUE), b""):
            hasher.update(bloque)
    return "sha256:" + hasher.hexdigest()


def _excluido(ruta: Path, excluidos: set[str]) -> bool:
    return any(parte in excluidos for parte in ruta.parts)


def generar(registro_path: Path, repo_root: Path) -> dict[str, str]:
    datos = yaml.safe_load(registro_path.read_text(encoding="utf-8"))
    excluidos: set[str] = set(datos.get("exclude_dirs", []))
    baseline: dict[str, str] = {}
    for nombre_sistema, sistema in datos.get("systems", {}).items():
        base = repo_root / sistema["base"]
        contador = 0
        for patron in sistema.get("patterns", []):
            for ruta in base.glob(patron):
                if not ruta.is_file() or _excluido(ruta, excluidos):
                    continue
                clave = ruta.relative_to(repo_root).as_posix()
                baseline[clave] = _hash_archivo(ruta)
                contador += 1
        print(f"AP-0121: {nombre_sistema}: {contador} archivos criticos")
    return baseline


def main() -> int:
    parser = argparse.ArgumentParser(description="AP-0121 baseline de archivos criticos")
    parser.add_argument("--registry", default=str(_REGISTRO_DEFECTO))
    parser.add_argument("--root", default=str(_REPO_DEFECTO))
    parser.add_argument("--out", default=str(_SALIDA_DEFECTO))
    args = parser.parse_args()

    baseline = generar(Path(args.registry), Path(args.root))
    salida = Path(args.out)
    salida.write_text(
        json.dumps(baseline, indent=2, sort_keys=True) + _SALTO, encoding="utf-8"
    )
    print(f"AP-0121: baseline con {len(baseline)} archivos criticos -> {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())