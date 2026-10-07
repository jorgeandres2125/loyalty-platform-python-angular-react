from typing import Final

from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad

# AP-0134: orden de severidad para el umbral de alertamiento.
RANGO_SEVERIDAD: Final[dict[SeveridadSeguridad, int]] = {
    SeveridadSeguridad.INFORMATIVA: 0,
    SeveridadSeguridad.BAJA: 1,
    SeveridadSeguridad.MEDIA: 2,
    SeveridadSeguridad.ALTA: 3,
    SeveridadSeguridad.CRITICA: 4,
}

# AP-0134: eventos de auditoria del propio alertador. Empiezan con este prefijo para que
# el AlertaHandler NUNCA los re-alerte (evita recursion infinita).
PREFIJO_EVENTO_ALERTA: Final[str] = "alerta_"
EVENTO_ALERTA_EMITIDA: Final[str] = "alerta_emitida"
EVENTO_ALERTA_NO_ENTREGADA: Final[str] = "alerta_no_entregada"
EVENTO_ALERTA_CANAL_LOG: Final[str] = "alerta_canal_log"
