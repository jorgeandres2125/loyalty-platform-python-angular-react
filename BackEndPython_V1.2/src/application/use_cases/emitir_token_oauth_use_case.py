from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from typing import Any

from src.application.dto.token_oauth_dto import TokenOAuthDTO
from src.domain.exceptions.audiencia_no_permitida import AudienciaNoPermitida
from src.infrastructure.security.jwt_handler import JWTHandler


class EmitirTokenOAuthUseCase:
    '''AP-0146: front de autenticacion propio (IdP estilo OAuth).

    Tras autenticarse el usuario en NUESTRO front (JWT), emite un access token JWT
    firmado con claims estandar (iss, aud, sub, scope, exp) para una aplicacion de
    terceros autorizada. Las credenciales del usuario nunca se exponen al tercero;
    este solo recibe el token que nuestro IdP firma.
    '''

    def __init__(
        self,
        jwt_handler: JWTHandler,
        issuer: str,
        audiencias_permitidas: Sequence[str],
        expire_minutes: int,
        scope_default: str,
    ) -> None:
        self._jwt: JWTHandler = jwt_handler
        self._issuer: str = issuer
        self._audiencias: frozenset[str] = frozenset(audiencias_permitidas)
        self._expire_minutes: int = expire_minutes
        self._scope_default: str = scope_default

    def emitir(
        self,
        sub: str,
        audiencia: str,
        roles: Sequence[str],
        scope: str | None = None,
    ) -> TokenOAuthDTO:
        if audiencia not in self._audiencias:
            raise AudienciaNoPermitida(audiencia)
        alcance: str = scope or self._scope_default
        payload: dict[str, Any] = {
            'iss': self._issuer,
            'aud': audiencia,
            'sub': sub,
            'scope': alcance,
            'roles': list(roles),
            'token_use': 'access',
        }
        access_token: str = self._jwt.encode(payload, expires_minutes=self._expire_minutes)
        expira_en: int = int(timedelta(minutes=self._expire_minutes).total_seconds())
        return TokenOAuthDTO(
            access_token=access_token,
            token_type='Bearer',
            expires_in=expira_en,
            scope=alcance,
            audience=audiencia,
        )
