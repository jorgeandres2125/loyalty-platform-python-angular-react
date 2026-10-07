from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class EstadoBloqueoResponse(BaseModel):
    """AP-0157: estado combinado de bloqueo de una cuenta (suave + duro).

    Expone ambos estados de forma independiente para monitoreo, soporte y auditoria. El
    bloqueo duro (is_hard_locked) tiene precedencia: si esta activo, la cuenta no autentica
    aunque el suave este ausente o expirado."""

    model_config = ConfigDict(extra="forbid")

    uid: int
    is_soft_locked: bool
    soft_lock_reason: str | None
    soft_lock_expiration_epoch: float | None
    is_hard_locked: bool
    hard_lock_reason: str | None
