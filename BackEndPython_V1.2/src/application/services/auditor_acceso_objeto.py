from __future__ import annotations

import logging

from src.application.services.servicio_auditoria import ServicioAuditoria
from src.domain.value_objects.accion_recurso import AccionRecurso
from src.domain.value_objects.resource_type import ResourceType
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.shared.constants.eventos_seguridad import (
    EVENTO_AUTORIZACION,
    LOGGER_SEGURIDAD,
    RESULTADO_EXITO,
    RESULTADO_FALLO,
)

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)
_ACCION_AUDIT: str = "acceso_objeto"


class AuditorAccesoObjeto:
    """AP-0055: registra cada decision de acceso a objeto sensible (ALLOW o DENY) en
    el historial de auditoria (AP-0028, fail-safe) y en el logger de seguridad
    (AP-0022, severidad ALTA en denegacion)."""

    def __init__(self, servicio_auditoria: ServicioAuditoria) -> None:
        self._auditoria: ServicioAuditoria = servicio_auditoria

    async def registrar(
        self,
        actor_uid: int,
        tipo: ResourceType,
        resource_id: str | None,
        accion: AccionRecurso,
        permitido: bool,
        motivo: str,
        modo: str,
    ) -> None:
        resultado: str = RESULTADO_EXITO if permitido else RESULTADO_FALLO
        severidad: SeveridadSeguridad = (
            SeveridadSeguridad.BAJA if permitido else SeveridadSeguridad.ALTA
        )
        _logger.log(
            logging.INFO if permitido else logging.WARNING,
            "AP-0055: acceso a objeto %s",
            "ALLOW" if permitido else "DENY",
            extra={
                "evento_seguridad": EVENTO_AUTORIZACION,
                "severidad": severidad.value,
                "resultado": resultado,
                "actor": str(actor_uid),
                "recurso_tipo": tipo.value,
                "recurso_id": resource_id or "",
                "accion": accion.value,
                "motivo": motivo,
                "modo": modo,
            },
        )
        await self._auditoria.registrar_async(
            accion=_ACCION_AUDIT,
            user_id=actor_uid,
            entidad=tipo.value,
            entidad_id=resource_id,
            detalle={
                "accion": accion.value,
                "permitido": permitido,
                "motivo": motivo,
                "modo": modo,
            },
            resultado=resultado,
        )
