"""Helpers para la autenticación basada en cookie (Medida A del plan de remediación).

El JWT se entrega en una cookie HttpOnly/Secure/SameSite (inaccesible a JavaScript),
acompañada de una cookie CSRF legible para el patrón double-submit. No define clases:
respeta la regla de "una clase por archivo" (cero clases) del proyecto.
"""
from __future__ import annotations

import secrets
from typing import Literal, cast

from fastapi import Response

from src.infrastructure.config.settings import Settings

_SAMESITE_VALIDOS: frozenset[str] = frozenset({"lax", "strict", "none"})


def generar_csrf_token() -> str:
    """Token CSRF aleatorio criptográficamente seguro (double-submit)."""
    return secrets.token_urlsafe(32)


def _samesite(settings: Settings) -> Literal["lax", "strict", "none"]:
    valor: str = settings.cookie_samesite.lower()
    if valor not in _SAMESITE_VALIDOS:
        return "lax"
    return cast(Literal["lax", "strict", "none"], valor)


def set_auth_cookies(
    response: Response,
    token: str,
    csrf_token: str,
    settings: Settings,
    max_age_seconds: int,
) -> None:
    """Fija la cookie de sesión (HttpOnly) y la cookie CSRF (legible por JS)."""
    dominio: str | None = settings.cookie_domain or None
    samesite: Literal["lax", "strict", "none"] = _samesite(settings)
    # Cookie de sesión: HttpOnly → el token no es accesible desde el DOM (AP-0093/0099).
    response.set_cookie(
        key=settings.cookie_auth_name,
        value=token,
        max_age=max_age_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=samesite,
        domain=dominio,
        path="/",
    )
    # Cookie CSRF: NO HttpOnly, para que el frontend la reenvíe en la cabecera (double-submit).
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=csrf_token,
        max_age=max_age_seconds,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=samesite,
        domain=dominio,
        path="/",
    )


def clear_auth_cookies(response: Response, settings: Settings) -> None:
    """Borra las cookies de sesión y CSRF (logout)."""
    dominio: str | None = settings.cookie_domain or None
    response.delete_cookie(settings.cookie_auth_name, domain=dominio, path="/")
    response.delete_cookie(settings.csrf_cookie_name, domain=dominio, path="/")
