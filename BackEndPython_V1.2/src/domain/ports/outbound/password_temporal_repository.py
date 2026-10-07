from __future__ import annotations

from typing import Protocol

from src.domain.entities.password_temporal_entity import PasswordTemporalEntity


class PasswordTemporalRepository(Protocol):
    """AP-0046, AP-0047 y AP-0048: puerto de salida de credenciales temporales.

    Contrato PEP 544 sobre la tabla lateral user_password_temporal; no toca
    dbo.users (propiedad de Drupal). Solo puede existir una temporal vigente por
    usuario: crear marca REEMPLAZADA a las previas ACTIVA o USADA en la misma
    transaccion. Un adaptador satisface el contrato por forma, sin heredar.
    """

    async def obtener_vigente(self, uid: int) -> PasswordTemporalEntity | None: ...

    async def crear(self, entidad: PasswordTemporalEntity) -> PasswordTemporalEntity: ...

    async def marcar_usada(self, temporal_id: int, usada_iso: str) -> None: ...

    async def marcar_consumida(self, temporal_id: int, consumida_iso: str) -> None: ...
