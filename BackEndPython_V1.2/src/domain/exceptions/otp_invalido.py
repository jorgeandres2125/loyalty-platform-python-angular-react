from __future__ import annotations


class OtpInvalido(Exception):
    """AP-0012: el codigo OTP de login es incorrecto, expiro o se agotaron los intentos."""

    def __init__(self, motivo: str, intentos_restantes: int | None = None) -> None:
        super().__init__(motivo)
        self.motivo: str = motivo
        self.intentos_restantes: int | None = intentos_restantes
