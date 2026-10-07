from __future__ import annotations


class TokenOidcInvalido(Exception):
    """AP-0010: el token OIDC no es valido (firma, emisor, audiencia, expiracion o algoritmo)."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo: str = motivo
