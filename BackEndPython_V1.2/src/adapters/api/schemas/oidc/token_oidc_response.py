from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TokenOidcResponse(BaseModel):
    """AP-0010: respuesta del endpoint de token estandar OIDC/OAuth2."""

    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str
    expires_in: int
    scope: str
