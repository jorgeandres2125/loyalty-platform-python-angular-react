from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TokenOAuthDTO:
    """AP-0146: access token estilo OAuth emitido por nuestro IdP para un tercero."""

    access_token: str
    token_type: str
    expires_in: int
    scope: str
    audience: str
