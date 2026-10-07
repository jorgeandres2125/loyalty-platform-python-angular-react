from __future__ import annotations

from pydantic import BaseModel


class TokenOAuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str
    audience: str
