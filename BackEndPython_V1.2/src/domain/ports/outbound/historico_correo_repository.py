from __future__ import annotations

from typing import Protocol

from src.domain.entities.historico_correo_entity import HistoricoCorreoEntity


class HistoricoCorreoRepository(Protocol):
    """Puerto de salida para registrar envíos de correo en `historico_correo`."""

    async def registrar_async(self, entity: HistoricoCorreoEntity) -> None: ...
