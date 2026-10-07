from __future__ import annotations

from datetime import date
from typing import Any, Protocol


class ReporteGenerator(Protocol):
    async def generar_hoja_vida_async(
        self,
        programa: int,
        subprograma: int | None,
        fecha_inicio: date | None,
        fecha_fin: date | None,
    ) -> bytes: ...

    async def generar_info_laboral_async(
        self,
        fecha_inicio: date | None,
        fecha_fin: date | None,
    ) -> bytes: ...

    async def generar_plantilla_participantes_async(
        self,
        programa: int,
        subprograma: int | None,
        fecha_inicio: date | None,
        fecha_fin: date | None,
    ) -> bytes: ...

    async def generar_info_tributaria_async(
        self,
        fecha_inicio: date | None,
        fecha_fin: date | None,
    ) -> bytes: ...

    async def generar_usuarios_migrados_async(
        self,
        fecha_inicio: date | None,
        fecha_fin: date | None,
    ) -> bytes: ...

    async def generar_default_async(
        self,
        programa: int,
        subprograma: int | None,
        fecha_inicio: date | None,
        fecha_fin: date | None,
    ) -> bytes: ...

    async def generar_estados_perfiles_async(
        self,
        programa: int,
        subprograma: int | None,
        fecha_inicio: date | None,
        fecha_fin: date | None,
        cedula: str | None,
        estado: int | None,
    ) -> bytes: ...

    async def obtener_preview_async(
        self,
        tipo: int,
        programa: int,
        subprograma: int | None,
        fecha_inicio: date | None,
        fecha_fin: date | None,
        cedula: str | None,
        estado: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[str], list[list[Any]], int]: ...
