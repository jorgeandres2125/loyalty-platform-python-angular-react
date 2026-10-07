"""Constantes del bloqueo suave y duro de cuentas (AP-0157)."""
from typing import Final

# Eventos de auditoria sobre el logger de seguridad (AP-0022).
EVENTO_BLOQUEO_DURO: Final[str] = "bloqueo_duro"
EVENTO_BLOQUEO_SUAVE_ADMIN: Final[str] = "bloqueo_suave_admin"

# Motivo por defecto del bloqueo suave AUTOMATICO (AP-0009). El bloqueo suave
# administrativo lleva el motivo que indique el operador.
MOTIVO_SOFT_AUTOMATICO: Final[str] = "Exceso de intentos fallidos"
