"""AP-0062 -- origen de secretos y nombres logicos de credenciales privilegiadas."""
from __future__ import annotations

from typing import Final

# Valor de Settings.secrets_provider que activa el broker PAM (el resto = proveedor de entorno).
PROVEEDOR_SECRETOS_PAM: Final[str] = "pam"

# Nombres logicos de los secretos de conexion a la BD (independientes del proveedor).
SECRETO_DB_USER: Final[str] = "db_user"
SECRETO_DB_PASSWORD: Final[str] = "db_password"
