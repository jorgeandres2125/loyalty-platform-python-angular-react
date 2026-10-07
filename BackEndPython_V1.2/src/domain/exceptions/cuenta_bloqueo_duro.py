from __future__ import annotations


class CuentaBloqueoDuro(Exception):
    """AP-0157: la cuenta tiene un bloqueo duro activo.

    Nunca autentica hasta que un administrador autorizado lo retire explicitamente. Tiene
    precedencia absoluta sobre el bloqueo suave (AP-0009)."""

    def __init__(self, motivo: str = "") -> None:
        self.motivo: str = motivo
        super().__init__("Cuenta con bloqueo duro activo")
