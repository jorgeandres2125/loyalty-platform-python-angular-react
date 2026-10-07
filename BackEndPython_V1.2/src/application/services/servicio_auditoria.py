from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from datetime import UTC, datetime

from src.domain.entities.registro_auditoria import RegistroAuditoria
from src.domain.ports.outbound.auditoria_escritor_gateway import AuditoriaEscritorGateway
from src.shared.constants.auditoria import RESULTADO_EXITO
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


class ServicioAuditoria:
    """AP-0028: registra acciones de usuario en el historial de auditoria (fail-safe).

    Construye el asiento y lo persiste via el gateway autonomo. Si la escritura falla, lo
    reporta al log de seguridad y NO propaga la excepcion, de modo que la operacion
    principal del usuario nunca se rompe por un fallo de auditoria.
    """

    def __init__(self, escritor: AuditoriaEscritorGateway) -> None:
        self._escritor: AuditoriaEscritorGateway = escritor

    async def registrar_async(
        self,
        accion: str,
        user_id: int | None = None,
        usuario: str = "",
        entidad: str | None = None,
        entidad_id: str | None = None,
        detalle: Mapping[str, object] | None = None,
        ip_origen: str | None = None,
        resultado: str = RESULTADO_EXITO,
    ) -> None:
        registro: RegistroAuditoria = RegistroAuditoria(
            accion=accion,
            user_id=user_id,
            usuario=usuario,
            entidad=entidad,
            entidad_id=entidad_id,
            detalle=self._serializar(detalle),
            ip_origen=ip_origen,
            resultado=resultado,
            creado_iso=datetime.now(UTC).isoformat(timespec="milliseconds"),
        )
        try:
            await self._escritor.guardar_async(registro)
        except Exception as exc:  # fail-safe: nunca romper la operacion principal
            _logger.warning("AP-0028 auditoria no registrada (%s): %s", accion, exc)

    @staticmethod
    def _serializar(detalle: Mapping[str, object] | None) -> str | None:
        if detalle is None:
            return None
        try:
            return json.dumps(detalle, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            return None
