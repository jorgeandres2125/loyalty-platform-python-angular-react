from __future__ import annotations


class CodigoInvalido(Exception):
    """El código de verificación no coincide, expiró o agotó los intentos (AP-0004)."""

    def __init__(self, motivo: str, intentos_restantes: int | None = None) -> None:
        super().__init__(motivo)
        self.motivo: str = motivo
        self.intentos_restantes: int | None = intentos_restantes
