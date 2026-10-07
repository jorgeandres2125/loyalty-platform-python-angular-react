from __future__ import annotations

from typing import Protocol


class SondaDisponibilidad(Protocol):
    """AP-0081: puerto de sondeo de disponibilidad de dependencias criticas.

    Lo implementan adaptadores de infraestructura (por ejemplo, un ping a la base
    de datos). El endpoint de readiness lo consulta para decidir si la replica
    esta lista para recibir trafico; si la dependencia no responde, la replica se
    saca del balanceo sin tumbar el proceso. Contrato estructural (PEP 544): el
    adaptador satisface el puerto por forma, sin heredar.
    """

    async def base_datos_disponible(self) -> bool:
        ...
