"""AP-0146: front de autenticacion propio (IdP estilo OAuth) para apps de terceros."""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from src.adapters.api.error_handlers import audiencia_no_permitida_handler
from src.adapters.api.routers import oauth_router
from src.application.use_cases.emitir_token_oauth_use_case import EmitirTokenOAuthUseCase
from src.domain.exceptions.audiencia_no_permitida import AudienciaNoPermitida
from src.infrastructure.config.dependencies import (
    get_emitir_token_oauth_uc,
    require_token,
)
from src.infrastructure.security.jwt_handler import JWTHandler

SL = chr(47)
_SECRET = "secreto-de-pruebas-oauth-123456"


def _uc() -> EmitirTokenOAuthUseCase:
    return EmitirTokenOAuthUseCase(
        jwt_handler=JWTHandler(_SECRET, "HS256"),
        issuer="sufi-auth",
        audiencias_permitidas=["sapin"],
        expire_minutes=15,
        scope_default="perfil incentivos",
    )


def test_emite_token_con_claims_oauth() -> None:
    dto = _uc().emitir(sub="123", audiencia="sapin", roles=["comisionista"])
    assert dto.token_type == "Bearer"
    assert dto.audience == "sapin"
    assert dto.expires_in == 900
    claims = jwt.get_unverified_claims(dto.access_token)
    assert claims["iss"] == "sufi-auth"
    assert claims["aud"] == "sapin"
    assert claims["sub"] == "123"
    assert claims["scope"] == "perfil incentivos"
    assert claims["roles"] == ["comisionista"]


def test_scope_personalizado() -> None:
    dto = _uc().emitir(sub="1", audiencia="sapin", roles=[], scope="solo-lectura")
    assert dto.scope == "solo-lectura"


def test_audiencia_no_permitida_lanza() -> None:
    with pytest.raises(AudienciaNoPermitida):
        _uc().emitir(sub="1", audiencia="app-desconocida", roles=[])


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(oauth_router.router, prefix=SL + "api" + SL + "v1" + SL + "oauth")
    app.add_exception_handler(AudienciaNoPermitida, audiencia_no_permitida_handler)
    app.dependency_overrides[require_token] = lambda: {"sub": "123", "roles": ["comisionista"]}
    app.dependency_overrides[get_emitir_token_oauth_uc] = lambda: _uc()
    return TestClient(app)


_RUTA = SL + "api" + SL + "v1" + SL + "oauth" + SL + "token"


def test_endpoint_emite_token_tras_login() -> None:
    r = _client().post(_RUTA, json={"audience": "sapin"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["token_type"] == "Bearer"
    assert cuerpo["audience"] == "sapin"
    assert cuerpo["access_token"]


def test_endpoint_rechaza_audiencia_no_permitida() -> None:
    r = _client().post(_RUTA, json={"audience": "otra-app"})
    assert r.status_code == 400
