from __future__ import annotations


class DesafioOobInvalido(Exception):
    """AP-0005: el desafio OOB no existe, expiro, ya se resolvio o el codigo es incorrecto."""

    def __init__(self, motivo: str, intentos_restantes: int | None = None) -> None:
        super().__init__(motivo)
        self.motivo: str = motivo
        self.intentos_restantes: int | None = intentos_restantes
