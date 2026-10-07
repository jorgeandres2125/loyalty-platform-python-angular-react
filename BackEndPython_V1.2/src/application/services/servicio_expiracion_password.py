from __future__ import annotations

import logging
from datetime import UTC, datetime

from src.domain.ports.outbound.password_expiracion_repository import (
    PasswordExpiracionRepository,
)
from src.domain.services.politica_expiracion_password import PoliticaExpiracionPassword
from src.domain.value_objects.aviso_expiracion_password import AvisoExpiracionPassword
from src.domain.value_objects.estado_credencial import EstadoCredencial
from src.domain.value_objects.estado_credencial_info import EstadoCredencialInfo

_logger: logging.Logger = logging.getLogger("sufi.expiracion_password")

# AP-0038: ante un fallo de lectura o sin linea base, se clasifica como VIGENTE para no
# dejar sin acceso a toda la plataforma por una incidencia de infraestructura (se
# prioriza disponibilidad sobre estrictez; el evento queda en el log). El reloj arranca
# en el primer login de cada usuario, por eso "sin base" equivale a "recien iniciado".
_ESTADO_VIGENTE_POR_DEFECTO: EstadoCredencialInfo = EstadoCredencialInfo(
    estado=EstadoCredencial.VIGENTE, dias_desde_vencimiento=0, dias_restantes_gracia=0
)


class ServicioExpiracionPassword:
    """AP-0037 y AP-0038: orquesta el reloj de vencimiento, el aviso previo y la
    clasificacion de estado (vigente, en gracia, fuera de gracia).

    Fail-safe: NUNCA rompe la operacion de negocio. Si la persistencia falla (por
    ejemplo, la migracion aun no corrio y la tabla no existe), registra una
    advertencia y sigue: evaluar_aviso devuelve None, evaluar_estado devuelve VIGENTE
    y las escrituras son no-op. Esto hace seguro desplegar la funcion antes o
    independientemente de la migracion.

    - asegurar_baseline: arranca el contador en el primer login tras habilitar la
      funcion (no pisa un valor existente).
    - registrar_cambio: reinicia el contador al cambiar la contrasena.
    - evaluar_aviso: solo lectura; aviso de proximidad al vencimiento (AP-0037).
    - evaluar_estado: solo lectura; estado respecto de la gracia (AP-0038).
    """

    def __init__(
        self,
        repo: PasswordExpiracionRepository,
        politica: PoliticaExpiracionPassword,
        habilitado: bool = True,
    ) -> None:
        self._repo: PasswordExpiracionRepository = repo
        self._politica: PoliticaExpiracionPassword = politica
        self._habilitado: bool = habilitado

    @staticmethod
    def _ahora(ahora: datetime | None) -> datetime:
        return ahora if ahora is not None else datetime.now(UTC).replace(tzinfo=None)

    async def asegurar_baseline(self, uid: int, ahora: datetime | None = None) -> None:
        if not self._habilitado:
            return
        try:
            await self._repo.asegurar_baseline(uid, self._ahora(ahora))
        except Exception as exc:  # noqa: BLE001 -- fail-safe, no rompe el login
            _logger.warning("AP-0037: no se pudo asegurar baseline uid=%s: %s", uid, exc)

    async def registrar_cambio(self, uid: int, ahora: datetime | None = None) -> None:
        if not self._habilitado:
            return
        try:
            await self._repo.registrar_cambio(uid, self._ahora(ahora))
        except Exception as exc:  # noqa: BLE001 -- fail-safe, no rompe el cambio
            _logger.warning("AP-0037: no se pudo registrar cambio uid=%s: %s", uid, exc)

    async def evaluar_aviso(
        self, uid: int, ahora: datetime | None = None
    ) -> AvisoExpiracionPassword | None:
        if not self._habilitado:
            return None
        try:
            cambiado_en: datetime | None = await self._repo.obtener_cambiado_en(uid)
        except Exception as exc:  # noqa: BLE001 -- fail-safe, no rompe la sesion
            _logger.warning("AP-0037: no se pudo leer baseline uid=%s: %s", uid, exc)
            return None
        if cambiado_en is None:
            return None
        return self._politica.evaluar(cambiado_en, self._ahora(ahora))

    async def cambiada_hoy(
        self, uid: int, tz: str, ahora: datetime | None = None
    ) -> bool:
        # AP-0043: True si la contrasena ya se cambio hoy (dia local de negocio).
        # Fail-open a False: una incidencia de BD no debe bloquear un cambio legitimo.
        try:
            cambiado_en: datetime | None = await self._repo.obtener_cambiado_en(uid)
        except Exception as exc:  # noqa: BLE001 -- fail-open, no bloquea el cambio
            _logger.warning("AP-0043: no se pudo leer baseline uid=%s: %s", uid, exc)
            return False
        if cambiado_en is None:
            return False
        return self._politica.es_mismo_dia_local(cambiado_en, self._ahora(ahora), tz)

    async def evaluar_estado(
        self, uid: int, ahora: datetime | None = None
    ) -> EstadoCredencialInfo:
        # AP-0038: clasifica el estado de la contrasena. Fail-open a VIGENTE (ver
        # nota del modulo) para que una incidencia de BD no bloquee el acceso.
        try:
            cambiado_en: datetime | None = await self._repo.obtener_cambiado_en(uid)
        except Exception as exc:  # noqa: BLE001 -- fail-open, no bloquea el login
            _logger.warning("AP-0038: no se pudo leer baseline uid=%s: %s", uid, exc)
            return _ESTADO_VIGENTE_POR_DEFECTO
        if cambiado_en is None:
            return _ESTADO_VIGENTE_POR_DEFECTO
        return self._politica.clasificar(cambiado_en, self._ahora(ahora))
