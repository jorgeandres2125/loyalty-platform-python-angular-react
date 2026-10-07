"""Constantes de la identificacion del equipo origen en autenticacion (AP-0014)."""
from typing import Final

# Evento de auditoria del dispositivo de autenticacion (sobre el logger de AP-0022).
EVENTO_DISPOSITIVO: Final[str] = "dispositivo_autenticacion"


# Longitud maxima del User-Agent que se conserva.
USER_AGENT_MAX: Final[int] = 512
