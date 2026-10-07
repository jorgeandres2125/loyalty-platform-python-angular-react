from __future__ import annotations

from dataclasses import dataclass

from src.domain.entities.registro_auditoria import RegistroAuditoria


@dataclass(frozen=True, slots=True)
class PaginaAuditoria:
    """AP-0028: una pagina de resultados del historial (items mas metadatos de paginacion)."""

    items: list[RegistroAuditoria]
    page: int
    page_size: int
    total: int
