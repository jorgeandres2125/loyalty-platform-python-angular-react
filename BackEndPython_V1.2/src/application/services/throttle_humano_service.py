from __future__ import annotations

import time

from src.domain.ports.outbound.intentos_login_store import IntentosLoginStore
from src.domain.value_objects.intentos_login import IntentosLogin


class ThrottleHumanoService:
    """Gating de humano por retrasos incrementales por acción + IP (AP-0019).

    A diferencia de `LoginThrottleService` (que cuenta solo los fallos de login),
    aquí se cuenta CADA intento de una acción pública sensible (registro, reset…)
    por IP. Los primeros `intentos_libres` no aplican retraso —no penaliza a un
    humano que hace 1-2 peticiones—; a partir de ahí el retraso crece `paso` por
    intento hasta `maximo`. La ventana de reinicio la da el TTL del store.

    Reutiliza el store TTL genérico (contador con caducidad) y el value object
    `IntentosLogin` de AP-0007: ambos son, estructuralmente, un contador por clave.
    """

    def __init__(
        self,
        store: IntentosLoginStore,
        intentos_libres: int,
        paso_segundos: int,
        maximo_segundos: int,
    ) -> None:
        self._store: IntentosLoginStore = store
        self._intentos_libres: int = intentos_libres
        self._paso_segundos: int = paso_segundos
        self._maximo_segundos: int = maximo_segundos

    async def registrar_intento_async(self, clave: str) -> int:
        """Suma un intento a la clave (acción|ip) y devuelve los segundos de espera."""
        previo: IntentosLogin | None = await self._store.obtener(clave)
        base: IntentosLogin = previo or IntentosLogin(conteo=0, actualizado_en_monotonic=0.0)
        actualizado: IntentosLogin = base.con_fallo(time.monotonic())
        await self._store.guardar(clave, actualizado)
        return self._retraso(actualizado.conteo)

    def _retraso(self, conteo: int) -> int:
        excedente: int = conteo - self._intentos_libres
        if excedente <= 0:
            return 0
        return min(excedente * self._paso_segundos, self._maximo_segundos)
