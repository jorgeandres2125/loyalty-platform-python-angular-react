from __future__ import annotations


class CustodiaInsuficiente(Exception):
    """AP-0015: no hay suficientes custodios o shares para reconstruir la clave, o el
    reparto es invalido."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo: str = motivo
