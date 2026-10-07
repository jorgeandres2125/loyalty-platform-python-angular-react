from __future__ import annotations

from typing import Protocol

from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity


class AsesorConsumoRepository(Protocol):
    """Puerto de salida — users_perfil_contacto (asesores Consumo, programa_id=2)."""

    async def listar_async(
        self,
        page: int,
        size: int,
        tipo_doc: str | None = None,
        documento: str | None = None,
    ) -> tuple[list[PerfilContactoEntity], int]: ...

    async def obtener_async(self, numero_documento: str) -> PerfilContactoEntity | None: ...
