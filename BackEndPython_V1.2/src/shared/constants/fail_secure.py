"""AP-0109 -- opciones por defecto seguras (fail-secure).

Cuando falta o es invalida una opcion critica, la aplicacion debe quedar en el
estado mas seguro (rechazar) en vez de uno permisivo. Estas constantes apoyan los
validadores de Settings que garantizan ese comportamiento.
"""
from __future__ import annotations

from typing import Final

# Cuentas de base de datos prohibidas en staging/produccion: superadmin, cuentas
# administrativas y los placeholders de las plantillas .env. Comparacion en
# minusculas y sin espacios. Nunca conectar como una de estas por configuracion.
USUARIOS_BD_PROHIBIDOS: Final[frozenset[str]] = frozenset(
    {
        "sa",
        "root",
        "admin",
        "administrator",
        "sysadmin",
        "dbo",
        "<staging-db-user>",
        "<prod-db-user>",
    }
)

# Bytes de aleatoriedad para la clave JWT efimera de desarrollo/test cuando no se
# configuro una. token_hex duplica el numero de caracteres (32 -> 64 hex).
JWT_SECRET_EPHEMERAL_BYTES: Final[int] = 32
