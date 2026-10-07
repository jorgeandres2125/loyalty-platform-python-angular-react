"""Constantes del bloqueo de cuenta por intentos fallidos de login (AP-0009)."""
from typing import Final

# Evento de auditoria del bloqueo de cuenta (sobre el logger de seguridad AP-0022).
EVENTO_BLOQUEO_CUENTA: Final[str] = "bloqueo_cuenta"
