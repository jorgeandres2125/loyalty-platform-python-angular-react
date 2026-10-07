#!/usr/bin/env python3
"""AP-0120: genera la linea base (baseline) de integridad de los archivos criticos de la app.

Recorre el directorio de codigo, calcula el hash SHA-256 de cada archivo y escribe un JSON
{ruta_relativa: "sha256:..."} que se embebe en la imagen y consume el self-check al arranque
(VerificadorIntegridadArchivos). Se ejecuta en el pipeline de CI, tras copiar el codigo y
antes de firmar la imagen.

Uso: generar_baseline_integridad.py <base_dir> <subdir_codigo> <salida_json>
Ejemplo (en el build): generar_baseline_integridad.py /app src integridad_baseline.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

_TAMANO_BLOQUE = 65536


def _hash_archivo(ruta: Path) -> str:
    hasher = hashlib.sha256()
    with open(ruta, "rb") as fh:
        for bloque in iter(lambda: fh.read(_TAMANO_BLOQUE), b""):
            hasher.update(bloque)
    return "sha256:" + hasher.hexdigest()


def main() -> int:
    base_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    subdir = sys.argv[2] if len(sys.argv) > 2 else "src"
    salida = sys.argv[3] if len(sys.argv) > 3 else "integridad_baseline.json"

    baseline: dict[str, str] = {}
    raiz = base_dir / subdir
    for ruta in sorted(raiz.rglob("*.py")):
        if "__pycache__" in ruta.parts:
            continue
        relativa = ruta.relative_to(base_dir).as_posix()
        baseline[relativa] = _hash_archivo(ruta)

    Path(salida).write_text(json.dumps(baseline, indent=2, sort_keys=True), encoding="utf-8")
    print(f"AP-0120: baseline con {len(baseline)} archivos criticos -> {salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())