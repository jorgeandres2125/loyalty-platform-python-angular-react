from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects.estado_sesion import EstadoSesion
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion


@dataclass
class SesionActiva:
    """AP-0130 y AP-0132: sesion registrada en el Session Registry, con sus metadatos y
    su ciclo de vida. El `sid` identifica la sesion de forma estable (el `jti` rota en
    cada renovacion, AP-0129). AP-0132 anade la fecha de expiracion y, al cerrarse, la
    fecha y el motivo de cierre, para dejar evidencia auditable del descarte."""

    sid: str
    uid: int
    jti_actual: str
    device_fp: str
    ip: str
    user_agent: str
    canal: bool
    inicio: datetime
    last_activity: datetime
    estado: EstadoSesion = EstadoSesion.ACTIVA
    fecha_expiracion: datetime | None = None
    fecha_cierre: datetime | None = None
    motivo_cierre: MotivoCierreSesion | None = None
