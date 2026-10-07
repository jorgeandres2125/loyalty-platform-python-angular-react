"""Medida C (AP-0147 / AP-0095) — cifra el PII de contacto restante en
users_perfil_contacto: direccion, telefono, celular, email.

Usa el motor genérico migration._cifrar_columnas. La cuenta bancaria
(numero_de_cuenta / tipo_de_cuenta) ya se cifró aparte en
migration/cifrar_cuenta_bancaria.py.

    python -m migration.cifrar_pii_contacto           # add+backfill+verify
    python -m migration.cifrar_pii_contacto --drop    # + F4 (drop texto plano)
"""
from __future__ import annotations

import sys
from typing import Final

from migration._cifrar_columnas import cifrar_columnas

COLUMNAS: Final[list[str]] = ["direccion", "telefono", "celular", "email"]


def main() -> None:
    cifrar_columnas(COLUMNAS, drop="--drop" in sys.argv)


if __name__ == "__main__":
    main()
