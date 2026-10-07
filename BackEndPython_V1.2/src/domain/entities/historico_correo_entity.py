from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class HistoricoCorreoEntity:
    """Fila del log de correos enviados (`historico_correo`).

    Reusa la forma del legado (hc_uid, tipo_correo, usuario_envio, usuario_destino,
    fecha, enviado). En 2019 la tabla gana PRIMARY KEY en `hc_uid` (ADR-07).
    """

    tipo_correo: str
    usuario_envio: str
    usuario_destino: str
    fecha: datetime
    enviado: bool
    hc_uid: int | None = None
