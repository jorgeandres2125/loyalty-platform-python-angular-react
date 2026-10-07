from __future__ import annotations


class FirmaInvalida(Exception):
    """AP-0006: la firma digital no es valida, o el material de clave es incorrecto."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo: str = motivo
