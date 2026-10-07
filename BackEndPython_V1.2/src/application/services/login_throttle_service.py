from __future__ import annotations

import time

from src.domain.ports.outbound.intentos_login_store import IntentosLoginStore
from src.domain.value_objects.intentos_login import IntentosLogin


class LoginThrottleService:
    """Retraso incremental ante fallos de autenticación (AP-0007).

    Mantiene, por clave (IP|usuario), el número de fallos consecutivos y deriva el
    retraso a aplicar: `min(conteo × paso, maximo)`. El conteo caduca por el TTL del
    store (ventana de reinicio) y se borra de inmediato tras un login exitoso.

    El servicio NO duerme: calcula y devuelve los segundos de espera. Quien orqueste
    el login (el caso de uso) ejecuta el `sleep`, de modo que los tests verifican la
    curva 5→30 sin coste de reloj.
    """

    def __init__(
        self,
        store: IntentosLoginStore,
        paso_segundos: int,
        maximo_segundos: int,
    ) -> None:
        self._store: IntentosLoginStore = store
        self._paso_segundos: int = paso_segundos
        self._maximo_segundos: int = maximo_segundos

    async def registrar_fallo_async(self, clave: str) -> int:
        """Suma un fallo a la clave y devuelve los segundos de espera a aplicar."""
        previo: IntentosLogin | None = await self._store.obtener(clave)
        base: IntentosLogin = previo or IntentosLogin(conteo=0, actualizado_en_monotonic=0.0)
        actualizado: IntentosLogin = base.con_fallo(time.monotonic())
        await self._store.guardar(clave, actualizado)
        return self._retraso(actualizado.conteo)

    async def reiniciar_async(self, clave: str) -> None:
        """Borra el conteo de fallos de la clave (login exitoso)."""
        await self._store.eliminar(clave)

    def _retraso(self, conteo: int) -> int:
        if conteo <= 0:
            return 0
        return min(conteo * self._paso_segundos, self._maximo_segundos)
