from __future__ import annotations


class SesionInvalida(Exception):
    """AP-0021: la credencial es invalida (revocada, version obsoleta o sesion cerrada)."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo: str = motivo
