from __future__ import annotations

from src.application.services.servicio_auditoria import ServicioAuditoria
from src.shared.constants.eventos_seguridad import RESULTADO_EXITO


async def auditar_operacion_critica(
    auditoria: ServicioAuditoria,
    actor_uid: int,
    accion: str,
    entidad: str,
    entidad_id: str,
) -> None:
    """AP-0060: registra en el historial de auditoria (AP-0028) una operacion critica
    de administracion de catalogos (crear o actualizar canales, oficinas, ejecutivos).
    ServicioAuditoria es fail-safe: un fallo de escritura del asiento nunca rompe la
    operacion de negocio que ya se completo."""
    await auditoria.registrar_async(
        accion=accion,
        user_id=actor_uid,
        entidad=entidad,
        entidad_id=entidad_id,
        resultado=RESULTADO_EXITO,
    )
