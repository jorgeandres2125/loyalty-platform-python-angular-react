from __future__ import annotations


class PasswordTemporalVencida(Exception):
    """AP-0048: la contrasena temporal presentada coincide pero ya expiro.

    Solo se lanza con match exacto del hash temporal, por lo que no sirve como
    oraculo de enumeracion de cuentas. El usuario debe solicitar la reemision a
    un administrador (la credencial permanente, si existe, sigue funcionando).
    """

    def __init__(self, expira_iso: str) -> None:
        super().__init__("contrasena temporal vencida")
        self.expira_iso: str = expira_iso
