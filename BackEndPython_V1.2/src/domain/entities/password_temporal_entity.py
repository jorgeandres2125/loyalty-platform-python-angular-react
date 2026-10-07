from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.estado_password_temporal import EstadoPasswordTemporal
from src.domain.value_objects.origen_password_temporal import OrigenPasswordTemporal


@dataclass(frozen=True)
class PasswordTemporalEntity:
    """AP-0046, AP-0047 y AP-0048: credencial temporal de un usuario.

    Guarda el hash bcrypt de la temporal, su origen (quien la emitio, desde donde y
    por que) y su ciclo de vida (emision, expiracion, primer uso y consumo). Los
    instantes son ISO-8601 UTC naive, convencion del proyecto.
    """

    uid: int
    hash_temporal: str
    emitida_por_uid: int
    emitida_por_usuario: str
    origen: OrigenPasswordTemporal
    emitida_iso: str
    expira_iso: str
    estado: EstadoPasswordTemporal
    motivo: str | None = None
    ip_emision: str | None = None
    usada_iso: str | None = None
    consumida_iso: str | None = None
    id: int | None = None
