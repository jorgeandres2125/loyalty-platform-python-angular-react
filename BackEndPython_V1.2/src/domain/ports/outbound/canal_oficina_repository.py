from __future__ import annotations

from typing import Protocol


class CanalOficinaRepository(Protocol):
    """Puerto — relación N:M canales_oficinas."""

    async def listar_oficinas_por_canal_async(self, cod_canales: int) -> list[int]: ...

    async def reemplazar_oficinas_de_canal_async(
        self, cod_canales: int, cod_oficinas_ids: list[int]
    ) -> None: ...

    async def listar_canales_por_oficina_async(self, cod_oficinas: int) -> list[int]: ...

    async def reemplazar_canales_de_oficina_async(
        self, cod_oficinas: int, cod_canales_ids: list[int]
    ) -> None: ...
