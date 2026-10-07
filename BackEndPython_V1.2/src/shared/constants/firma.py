"""Constantes de la firma digital de informacion y transacciones sensibles (AP-0006)."""
from typing import Final

# Evento de auditoria del subsistema de firma (sobre el logger de seguridad AP-0022).
EVENTO_FIRMA: Final[str] = "firma_digital"

# Valor raiz de la cadena de evidencias (hash_anterior de la primera evidencia).
HASH_GENESIS: Final[str] = "0" * 64
