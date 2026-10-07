from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RegistroAuditoria:
    """AP-0028: un asiento del historial de auditoria (una accion de un usuario).

    Registra quien (user_id, usuario), que (accion), sobre que (entidad, entidad_id), el
    detalle opcional (JSON con antes y despues), el origen (ip_origen), el resultado y el
    instante en ISO 8601. El instante se guarda como texto para no depender de conversiones
    de fecha del proveedor (mismo criterio que AP-0014).
    """

    accion: str
    usuario: str = ""
    user_id: int | None = None
    entidad: str | None = None
    entidad_id: str | None = None
    detalle: str | None = None
    ip_origen: str | None = None
    resultado: str = "exito"
    creado_iso: str = ""
    id: int | None = None
