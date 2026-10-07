from __future__ import annotations

import logging
from typing import Final

from src.domain.exceptions.permiso_objeto_excesivo import PermisoObjetoExcesivo
from src.domain.ports.outbound.sonda_permisos_objeto import SondaPermisosObjeto
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD
from src.shared.constants.minimo_privilegio import EVENTO_PERMISO_OBJETO

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)
_ENTORNOS_ENFORCE: Final[frozenset[str]] = frozenset({"staging", "production"})


class VerificadorPermisosObjeto:
    """AP-0061: en el arranque comprueba que la cuenta de la app no herede permisos excesivos
    sobre objetos (p. ej. EXECUTE a nivel de base de datos, que alcanza a todo procedimiento o
    funcion actual y futuro). Complementa a AP-0056 (membresia de rol del principal) con la
    dimension de objetos nuevos. En staging y produccion aborta el arranque (fail-fast); en
    dev y test registra una advertencia auditada. El sondeo es best-effort: un fallo no rompe
    el arranque.
    """

    def __init__(
        self, sonda: SondaPermisosObjeto, app_env: str, habilitado: bool
    ) -> None:
        self._sonda: SondaPermisosObjeto = sonda
        self._app_env: str = app_env
        self._habilitado: bool = habilitado

    async def verificar(self) -> None:
        if not self._habilitado:
            return
        try:
            anomalias: list[str] = await self._sonda.anomalias_minimo_privilegio()
        except Exception as exc:  # noqa: BLE001 -- best-effort: no romper el arranque
            _logger.warning(
                "AP-0061: no se pudo verificar el minimo privilegio de objetos de BD: %s",
                exc,
                extra={
                    "evento_seguridad": EVENTO_PERMISO_OBJETO,
                    "severidad": SeveridadSeguridad.MEDIA.value,
                },
            )
            return
        if not anomalias:
            _logger.info(
                "AP-0061: los objetos de BD operan con minimo privilegio.",
                extra={
                    "evento_seguridad": EVENTO_PERMISO_OBJETO,
                    "severidad": SeveridadSeguridad.BAJA.value,
                },
            )
            return
        mensaje: str = (
            "AP-0061: permisos excesivos sobre objetos de BD: " + "; ".join(anomalias)
        )
        if self._app_env in _ENTORNOS_ENFORCE:
            _logger.critical(
                mensaje,
                extra={
                    "evento_seguridad": EVENTO_PERMISO_OBJETO,
                    "severidad": SeveridadSeguridad.CRITICA.value,
                },
            )
            raise PermisoObjetoExcesivo(mensaje)
        _logger.warning(
            mensaje,
            extra={
                "evento_seguridad": EVENTO_PERMISO_OBJETO,
                "severidad": SeveridadSeguridad.ALTA.value,
            },
        )
