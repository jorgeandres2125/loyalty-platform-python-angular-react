from __future__ import annotations

import logging
from typing import Final

from src.domain.exceptions.privilegio_bd_excesivo import PrivilegioBdExcesivo
from src.domain.ports.outbound.sonda_privilegio_bd import SondaPrivilegioBd
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD
from src.shared.constants.minimo_privilegio import EVENTO_PRIVILEGIO_BD

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)
_ENTORNOS_ENFORCE: Final[frozenset[str]] = frozenset({"staging", "production"})


class VerificadorPrivilegioBd:
    """AP-0056: en el arranque comprueba que el principal de BD conectado por la app no
    pertenezca a roles privilegiados. Es defensa en profundidad sobre AP-0109 (que solo
    valida el nombre configurado): detecta el caso de un principal privilegiado real (p. ej.
    un 'sa' renombrado). En staging y produccion aborta el arranque (fail-fast); en dev y
    test registra una advertencia auditada. El sondeo es best-effort: un fallo de conexion
    no rompe el arranque.
    """

    def __init__(self, sonda: SondaPrivilegioBd, app_env: str, habilitado: bool) -> None:
        self._sonda: SondaPrivilegioBd = sonda
        self._app_env: str = app_env
        self._habilitado: bool = habilitado

    async def verificar(self) -> None:
        if not self._habilitado:
            return
        try:
            roles: list[str] = await self._sonda.roles_privilegiados()
        except Exception as exc:  # noqa: BLE001 -- best-effort: no romper el arranque
            _logger.warning(
                "AP-0056: no se pudo verificar el privilegio del principal de BD: %s",
                exc,
                extra={
                    "evento_seguridad": EVENTO_PRIVILEGIO_BD,
                    "severidad": SeveridadSeguridad.MEDIA.value,
                },
            )
            return
        if not roles:
            _logger.info(
                "AP-0056: el principal de BD opera con minimo privilegio.",
                extra={
                    "evento_seguridad": EVENTO_PRIVILEGIO_BD,
                    "severidad": SeveridadSeguridad.BAJA.value,
                },
            )
            return
        mensaje: str = (
            "AP-0056: el principal de BD pertenece a roles privilegiados ("
            + ", ".join(roles)
            + "); viola el minimo privilegio (la app no debe conectar como sa ni db_owner)."
        )
        if self._app_env in _ENTORNOS_ENFORCE:
            _logger.critical(
                mensaje,
                extra={
                    "evento_seguridad": EVENTO_PRIVILEGIO_BD,
                    "severidad": SeveridadSeguridad.CRITICA.value,
                },
            )
            raise PrivilegioBdExcesivo(mensaje)
        _logger.warning(
            mensaje,
            extra={
                "evento_seguridad": EVENTO_PRIVILEGIO_BD,
                "severidad": SeveridadSeguridad.ALTA.value,
            },
        )
