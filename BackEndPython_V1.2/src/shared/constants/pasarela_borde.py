"""AP-0064 -- consumo exclusivo a traves del intermediario seguro (WAF, proxy, gateway)."""
from __future__ import annotations

from typing import Final

_S: Final[str] = chr(47)

# Evento de seguridad para la trazabilidad del enforcement de borde.
EVENTO_PASARELA_BORDE: Final[str] = "pasarela_borde"

# Nombre por defecto de la cabecera que inyecta el intermediario seguro (proxy o gateway).
# Configurable por Settings.edge_gateway_header (distintos edges usan nombres distintos).
HEADER_EDGE_GATEWAY_DEFECTO: Final[str] = "X-Edge-Gateway"

# Rutas internas exentas (sondas de salud del balanceador). Construidas sin barra literal.
RUTAS_EXENTAS_BORDE: Final[tuple[str, ...]] = (
    _S + "api" + _S + "v1" + _S + "health",
    _S + "health",
)
