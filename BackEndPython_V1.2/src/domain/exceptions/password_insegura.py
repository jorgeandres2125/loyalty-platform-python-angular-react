from __future__ import annotations


class PasswordInsegura(ValueError):
    """La contrasena propuesta esta en la lista de contrasenas inseguras conocidas
    o coincide con datos contextuales del usuario (AP-0159)."""

    def __init__(self, motivo: str = "Contrasena insegura o comun") -> None:
        super().__init__(motivo)
        self.motivo: str = motivo
