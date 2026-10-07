from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntentosLogin:
    """Registro inmutable de fallos de login consecutivos para una clave (AP-0007).

    `conteo` acumula los fallos consecutivos de una clave (IP|usuario).
    `actualizado_en_monotonic` (reloj monótono) marca el último fallo; el adaptador
    de almacenamiento usa el TTL como ventana deslizante para reiniciar el conteo.
    """

    conteo: int
    actualizado_en_monotonic: float

    def con_fallo(self, ahora_monotonic: float) -> IntentosLogin:
        return IntentosLogin(
            conteo=self.conteo + 1,
            actualizado_en_monotonic=ahora_monotonic,
        )
