"""Constantes de la doble custodia de credenciales criticas (AP-0015)."""
from typing import Final

# Evento de auditoria de la doble custodia de la clave (sobre el logger de AP-0022).
EVENTO_CUSTODIA: Final[str] = "doble_custodia_clave"

# Umbral por defecto: se requieren 2 custodios (2-of-N).
CUSTODIA_UMBRAL_DEFECTO: Final[int] = 2
