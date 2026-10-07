from __future__ import annotations

import logging
import time
from collections.abc import Callable

from src.domain.entities.bloqueo_cuenta import BloqueoCuenta
from src.domain.exceptions.cuenta_bloqueada import CuentaBloqueada
from src.domain.ports.outbound.bloqueo_cuenta_repository import BloqueoCuentaRepository
from src.shared.constants.bloqueo_cuenta import EVENTO_BLOQUEO_CUENTA
from src.shared.constants.bloqueo_duro import EVENTO_BLOQUEO_SUAVE_ADMIN
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


class ServicioBloqueoCuenta:
    """AP-0009: bloqueo de cuenta ante intentos fallidos de autenticacion.

    Cuenta los fallos consecutivos por cuenta (nombre de usuario normalizado) y bloquea
    al alcanzar el maximo configurado. Con desbloqueo automatico la cuenta se libera al
    vencer la duracion; un login exitoso reinicia el contador. Todo es configurable por
    entorno y se audita en el logger de seguridad (AP-0022). Deshabilitado, todas las
    operaciones son no-op (el login se comporta como antes).
    """

    def __init__(
        self,
        repo: BloqueoCuentaRepository,
        enabled: bool,
        max_intentos: int,
        duracion_minutos: int,
        auto_unlock: bool,
        reset_on_success: bool,
        count_non_existing: bool,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._repo: BloqueoCuentaRepository = repo
        self._enabled: bool = enabled
        self._max_intentos: int = max_intentos
        self._duracion_minutos: int = duracion_minutos
        self._auto_unlock: bool = auto_unlock
        self._reset_on_success: bool = reset_on_success
        self._count_non_existing: bool = count_non_existing
        self._clock: Callable[[], float] = clock

    async def verificar_no_bloqueada(self, clave: str) -> None:
        """Lanza CuentaBloqueada si la cuenta esta bloqueada y aun vigente.

        Si el desbloqueo automatico esta activo y la duracion ya vencio, libera la
        cuenta y deja pasar (auto-unlock)."""
        if not self._enabled:
            return
        estado: BloqueoCuenta | None = await self._repo.obtener(clave)
        if estado is None or not estado.bloqueada:
            return
        ahora: float = self._clock()
        if (
            self._auto_unlock
            and estado.expira_en_epoch > 0.0
            and ahora >= estado.expira_en_epoch
        ):
            await self._repo.eliminar(clave)
            _logger.info(
                "AP-0009 desbloqueo automatico clave=%s",
                clave,
                extra=self._campos("exito", clave),
            )
            return
        restantes: int | None = (
            max(0, int(estado.expira_en_epoch - ahora))
            if estado.expira_en_epoch > 0.0
            else None
        )
        raise CuentaBloqueada(segundos_restantes=restantes)

    async def registrar_fallo(self, clave: str, existe: bool) -> None:
        """Suma un fallo a la cuenta y la bloquea al alcanzar el maximo configurado."""
        if not self._enabled:
            return
        if not existe and not self._count_non_existing:
            return
        estado: BloqueoCuenta = (
            await self._repo.obtener(clave)
        ) or BloqueoCuenta.inicial(clave)
        if estado.bloqueada:
            return
        conteo: int = estado.conteo_fallos + 1
        if conteo >= self._max_intentos:
            ahora: float = self._clock()
            expira: float = (
                ahora + self._duracion_minutos * 60 if self._auto_unlock else 0.0
            )
            nuevo: BloqueoCuenta = estado.con_fallo().bloqueada_hasta(ahora, expira)
            _logger.warning(
                "AP-0009 cuenta bloqueada clave=%s fallos=%d",
                clave,
                conteo,
                extra=self._campos("fallo", clave),
            )
        else:
            nuevo = estado.con_fallo()
        await self._repo.guardar(nuevo)

    async def registrar_exito(self, clave: str) -> None:
        """Reinicia el contador de fallos tras un login exitoso (si esta configurado)."""
        if not self._enabled or not self._reset_on_success:
            return
        await self._repo.eliminar(clave)

    async def desbloquear(self, clave: str) -> None:
        """Desbloqueo manual (administrador): libera la cuenta y reinicia el contador."""
        await self._repo.eliminar(clave)
        _logger.info(
            "AP-0009 desbloqueo manual clave=%s", clave, extra=self._campos("exito", clave)
        )

    async def bloquear_manual(
        self, clave: str, duracion_minutos: int, motivo: str
    ) -> None:
        """AP-0157: bloqueo suave administrativo (suspension temporal u operativa).
        Independiente del conteo de fallos (AP-0009); expira tras la duracion indicada."""
        ahora: float = self._clock()
        expira: float = ahora + duracion_minutos * 60
        base: BloqueoCuenta = (
            await self._repo.obtener(clave)
        ) or BloqueoCuenta.inicial(clave)
        nuevo: BloqueoCuenta = base.bloqueada_hasta(ahora, expira).con_motivo(motivo)
        await self._repo.guardar(nuevo)
        _logger.warning(
            "AP-0157 bloqueo suave administrativo clave=%s",
            clave,
            extra={
                "evento_seguridad": EVENTO_BLOQUEO_SUAVE_ADMIN,
                "resultado": "exito",
                "actor": clave,
            },
        )

    async def consultar(self, clave: str) -> BloqueoCuenta | None:
        """AP-0157: estado del bloqueo suave vigente (aplica auto-unlock si expiro).
        Soporte del endpoint de estado y de la trazabilidad."""
        estado: BloqueoCuenta | None = await self._repo.obtener(clave)
        if estado is None:
            return None
        if (
            estado.bloqueada
            and self._auto_unlock
            and estado.expira_en_epoch > 0.0
            and self._clock() >= estado.expira_en_epoch
        ):
            await self._repo.eliminar(clave)
            return None
        return estado

    @staticmethod
    def _campos(resultado: str, clave: str) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_BLOQUEO_CUENTA,
            "resultado": resultado,
            "actor": clave,
        }
