"""AP-0056 -- roles de BD privilegiados incompatibles con el minimo privilegio del runtime.

Apoya el verificador de arranque que comprueba que el principal de BD conectado por la app
no pertenezca a roles administrativos. Complementa a AP-0109 (que valida el nombre
configurado) con una verificacion del privilegio real.
"""
from __future__ import annotations

from typing import Final

# Rol de servidor (se consulta con IS_SRVROLEMEMBER).
ROL_SERVIDOR_SYSADMIN: Final[str] = "sysadmin"

# Roles de base de datos (se consultan con IS_ROLEMEMBER). Su pertenencia implica
# privilegio excesivo para la cuenta de EJECUCION de la aplicacion.
ROLES_BD_PRIVILEGIADOS: Final[tuple[str, ...]] = (
    "db_owner",
    "db_securityadmin",
    "db_accessadmin",
    "db_ddladmin",
)

EVENTO_PRIVILEGIO_BD: Final[str] = "privilegio_bd"

# AP-0061: minimo privilegio sobre objetos nuevos (complementa AP-0056). El EXECUTE a nivel
# de base de datos es el permiso heredado que alcanza a todo procedimiento o funcion futuro.
ANOMALIA_EXECUTE_BD: Final[str] = (
    "EXECUTE a nivel de base de datos: la cuenta de la app puede ejecutar cualquier "
    "procedimiento o funcion, actual o futuro; viola el minimo privilegio de objetos nuevos"
)
EVENTO_PERMISO_OBJETO: Final[str] = "permiso_objeto"
