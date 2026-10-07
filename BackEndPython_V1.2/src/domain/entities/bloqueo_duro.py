from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BloqueoDuro:
    """AP-0157: bloqueo duro (administrativo o de seguridad) de una cuenta, por uid.

    A diferencia del bloqueo suave (AP-0009), no expira automaticamente y solo lo retira
    personal autorizado (permiso USUARIOS_HARDLOCK_GESTIONAR). Tiene precedencia absoluta
    en el login: si esta activo, la cuenta nunca autentica, independientemente de cualquier
    otro estado. Es independiente del bloqueo suave: ambos pueden coexistir.
    """

    uid: int
    activo: bool
    motivo: str
    bloqueado_en_epoch: float
    bloqueado_por_uid: int
