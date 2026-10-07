from __future__ import annotations

import logging
import time
from collections.abc import Callable

from src.domain.entities.bloqueo_duro import BloqueoDuro
from src.domain.exceptions.cuenta_bloqueo_duro import CuentaBloqueoDuro
from src.domain.ports.outbound.bloqueo_duro_repository import BloqueoDuroRepository
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.shared.constants.bloqueo_duro import EVENTO_BLOQUEO_DURO
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


class ServicioBloqueoDuro:
    """AP-0157: bloqueo duro (administrativo o de seguridad) de cuentas.

    Independiente del bloqueo suave (AP-0009) y con precedencia absoluta: el login lo
    verifica antes que el suave y antes de validar la credencial. No expira: solo lo
    retira personal con el permiso USUARIOS_HARDLOCK_GESTIONAR. Todas las acciones se
    auditan en el logger de seguridad (AP-0022) con severidad ALTA (AP-0023). Deshabilitado,
    verificar_no_bloqueada es no-op.
    """

    def __init__(
        self,
        repo: BloqueoDuroRepository,
        enabled: bool = True,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._repo: BloqueoDuroRepository = repo
        self._enabled: bool = enabled
        self._clock: Callable[[], float] = clock

    async def verificar_no_bloqueada(self, uid: int) -> None:
        """Lanza CuentaBloqueoDuro si la cuenta tiene un bloqueo duro activo."""
        if not self._enabled:
            return
        estado: BloqueoDuro | None = await self._repo.obtener(uid)
        if estado is not None and estado.activo:
            _logger.warning(
                "AP-0157 acceso denegado por bloqueo duro uid=%s",
                uid,
                extra=self._campos("fallo", uid),
            )
            raise CuentaBloqueoDuro(motivo=estado.motivo)

    async def aplicar(self, uid: int, motivo: str, por_uid: int) -> BloqueoDuro:
        """Aplica un bloqueo duro (administrativo). No altera el bloqueo suave."""
        estado: BloqueoDuro = BloqueoDuro(
            uid=uid,
            activo=True,
            motivo=motivo,
            bloqueado_en_epoch=self._clock(),
            bloqueado_por_uid=por_uid,
        )
        await self._repo.guardar(estado)
        _logger.warning(
            "AP-0157 bloqueo duro aplicado uid=%s por=%s",
            uid,
            por_uid,
            extra=self._campos("exito", uid),
        )
        return estado

    async def remover(self, uid: int, por_uid: int) -> None:
        """Retira el bloqueo duro. Solo personal autorizado. No toca el bloqueo suave."""
        await self._repo.eliminar(uid)
        _logger.warning(
            "AP-0157 bloqueo duro removido uid=%s por=%s",
            uid,
            por_uid,
            extra=self._campos("exito", uid),
        )

    async def consultar(self, uid: int) -> BloqueoDuro | None:
        """Estado del bloqueo duro para el endpoint de consulta y la trazabilidad."""
        return await self._repo.obtener(uid)

    @staticmethod
    def _campos(resultado: str, uid: int) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_BLOQUEO_DURO,
            "severidad": SeveridadSeguridad.ALTA.value,
            "resultado": resultado,
            "actor": str(uid),
        }
