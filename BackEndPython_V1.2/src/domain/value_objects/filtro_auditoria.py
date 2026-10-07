from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FiltroAuditoria:
    """AP-0028: filtros y paginacion del historial (rango de fechas ISO y tipo de accion)."""

    page: int
    page_size: int
    accion: str | None = None
    desde_iso: str | None = None
    hasta_iso: str | None = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size
