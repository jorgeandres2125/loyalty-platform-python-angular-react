"""Constantes de validacion de sesion y revocacion de credenciales (AP-0021)."""
from typing import Final

# Claims anadidos al JWT para la revalidacion por peticion.
CLAIM_JTI: Final[str] = "jti"
CLAIM_TOKEN_VERSION: Final[str] = "tv"
CLAIM_AUTH_EPOCH: Final[str] = "auth_epoch"
# AP-0130: identificador de sesion (estable entre renovaciones, a diferencia del jti).
CLAIM_SID: Final[str] = "sid"

# Version inicial de credencial (todo usuario nace en 1; se incrementa al revocar).
TOKEN_VERSION_INICIAL: Final[int] = 1

# Evento de auditoria de la validacion de sesion (sobre el logger de seguridad AP-0022).
EVENTO_SESION: Final[str] = "validacion_sesion"
# AP-0130: evento de auditoria de sesiones concurrentes.
EVENTO_SESION_CONCURRENTE: Final[str] = "sesion_concurrente"
