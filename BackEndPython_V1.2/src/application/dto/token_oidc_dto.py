from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenOidcDTO:
    """AP-0010: token estandar OIDC/OAuth2 emitido."""

    access_token: str
    token_type: str
    expires_in: int
    scope: str
