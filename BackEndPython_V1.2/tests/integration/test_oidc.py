from __future__ import annotations

import time

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt as jose_jwt

from src.adapters.api.routers import oidc_router
from src.application.services.validador_token_estandar import ValidadorTokenEstandar
from src.application.use_cases.emitir_token_oidc_use_case import EmitirTokenOidcUseCase
from src.domain.exceptions.token_oidc_invalido import TokenOidcInvalido
from src.infrastructure.config.dependencies import (
    get_emitir_token_oidc_uc,
    get_validador_token_estandar,
    require_token,
)
from src.infrastructure.security.proveedor_clave_oidc_es256 import ProveedorClaveOidcEs256

SL = chr(47)
_ISS = "sufi-iss"
_AUD = "sufi-aud"


def _prov() -> ProveedorClaveOidcEs256:
    return ProveedorClaveOidcEs256(None)


def _val(prov: ProveedorClaveOidcEs256) -> ValidadorTokenEstandar:
    return ValidadorTokenEstandar(proveedor=prov, issuer=_ISS, audiencia=_AUD)


class TestProveedorClaveOidc:
    def test_jwks_estructura(self) -> None:
        prov = _prov()
        keys = prov.jwks()["keys"]
        assert isinstance(keys, list)
        assert keys[0]["kty"] == "EC"
        assert keys[0]["crv"] == "P-256"
        assert keys[0]["alg"] == "ES256"
        assert keys[0]["kid"] == prov.kid

    def test_kid_estable_por_clave(self) -> None:
        pem = _prov()._privada_pem.encode("ascii")
        assert ProveedorClaveOidcEs256(pem).kid == ProveedorClaveOidcEs256(pem).kid

    def test_pem_invalido(self) -> None:
        with pytest.raises(TokenOidcInvalido):
            ProveedorClaveOidcEs256(b"no es una clave")


class TestValidadorTokenEstandar:
    def _claims(self, iss: str = _ISS, aud: str = _AUD, delta: int = 60) -> dict[str, object]:
        ahora = int(time.time())
        return {"iss": iss, "aud": aud, "sub": "1", "iat": ahora, "exp": ahora + delta}

    def test_token_valido(self) -> None:
        prov = _prov()
        token = prov.firmar(self._claims())
        assert _val(prov).validar(token)["sub"] == "1"

    def test_issuer_incorrecto(self) -> None:
        prov = _prov()
        token = prov.firmar(self._claims(iss="otro-iss"))
        with pytest.raises(TokenOidcInvalido):
            _val(prov).validar(token)

    def test_audiencia_incorrecta(self) -> None:
        prov = _prov()
        token = prov.firmar(self._claims(aud="otra-aud"))
        with pytest.raises(TokenOidcInvalido):
            _val(prov).validar(token)

    def test_token_expirado(self) -> None:
        prov = _prov()
        token = prov.firmar(self._claims(delta=-10))
        with pytest.raises(TokenOidcInvalido):
            _val(prov).validar(token)

    def test_algoritmo_simetrico_rechazado(self) -> None:
        prov = _prov()
        ahora = int(time.time())
        hs = jose_jwt.encode(
            {"iss": _ISS, "aud": _AUD, "sub": "1", "exp": ahora + 60},
            "secreto-simetrico-cualquiera",
            algorithm="HS256",
        )
        with pytest.raises(TokenOidcInvalido):
            _val(prov).validar(hs)

    def test_firma_de_otra_clave_rechazada(self) -> None:
        emisor = _prov()
        otro_validador = _val(_prov())
        token = emisor.firmar(self._claims())
        with pytest.raises(TokenOidcInvalido):
            otro_validador.validar(token)


class TestEmisor:
    def test_emitir_token_estandar(self) -> None:
        prov = _prov()
        uc = EmitirTokenOidcUseCase(
            proveedor=prov, issuer=_ISS, audiencia=_AUD, ttl_segundos=900, scope_default="openid"
        )
        dto = uc.emitir(sub="42", roles=["comisionista"])
        assert dto.token_type == "Bearer"
        assert dto.expires_in == 900
        claims = _val(prov).validar(dto.access_token)
        assert claims["sub"] == "42"
        assert claims["iss"] == _ISS
        assert claims["aud"] == _AUD
        assert claims["roles"] == ["comisionista"]


class TestEndpoints:
    def test_discovery_jwks_y_token(self) -> None:
        mini = FastAPI()
        mini.include_router(oidc_router.router)
        mini.dependency_overrides[require_token] = lambda: {"sub": "42", "roles": ["comisionista"]}
        cliente = TestClient(mini)

        disc = cliente.get(SL + ".well-known" + SL + "openid-configuration")
        assert disc.status_code == 200
        cuerpo = disc.json()
        assert cuerpo["issuer"]
        assert cuerpo["jwks_uri"].endswith(SL + ".well-known" + SL + "jwks.json")
        assert "ES256" in cuerpo["id_token_signing_alg_values_supported"]

        jw = cliente.get(SL + ".well-known" + SL + "jwks.json")
        assert jw.status_code == 200
        assert jw.json()["keys"][0]["kty"] == "EC"

        tok = cliente.post(SL + "api" + SL + "v1" + SL + "oidc" + SL + "token")
        assert tok.status_code == 200
        access = tok.json()["access_token"]
        claims = get_validador_token_estandar().validar(access)
        assert claims["sub"] == "42"


class TestRequireTokenAceptaEstandar:
    def test_token_estandar_autentica_ruta_protegida(self) -> None:
        mini = FastAPI()

        @mini.get(SL + "protegido", dependencies=[Depends(require_token)])
        def protegido() -> dict[str, bool]:
            return {"ok": True}

        cliente = TestClient(mini)
        assert cliente.get(SL + "protegido").status_code == 401

        dto = get_emitir_token_oidc_uc().emitir(sub="7", roles=["comisionista"])
        r = cliente.get(
            SL + "protegido", headers={"Authorization": "Bearer " + dto.access_token}
        )
        assert r.status_code == 200
