from __future__ import annotations

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.main import app as app_real
from src.adapters.api.routers import firma_router
from src.application.services.authorization_service import AuthorizationService
from src.application.services.permission_evaluator import PermissionEvaluator
from src.application.use_cases.firma_digital_use_case import FirmaDigitalUseCase
from src.domain.exceptions.firma_invalida import FirmaInvalida
from src.infrastructure.config.dependencies import (
    get_authorization_service,
    get_firma_digital_uc,
    require_token,
)
from src.infrastructure.external.in_memory_evidencia_firma_store import (
    InMemoryEvidenciaFirmaStore,
)
from src.infrastructure.security.firmador_es256 import FirmadorEs256

SL = chr(47)


def _authz_off() -> AuthorizationService:
    # AP-0055: modo off corto-circuita antes de tocar ownership o auditoria; evita la
    # BD en la mini-app. La firma es autoservicio (ownership_required=False).
    return AuthorizationService(PermissionEvaluator(), None, None, "off")  # type: ignore[arg-type]


def _pem() -> bytes:
    clave = ec.generate_private_key(ec.SECP256R1())
    return clave.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


def _uc(firmador=None):
    firmador = firmador or FirmadorEs256(None)
    store = InMemoryEvidenciaFirmaStore()
    return FirmaDigitalUseCase(firmador=firmador, evidencia_store=store), store


class TestFirmadorEs256:
    def test_firma_y_verifica(self) -> None:
        f = FirmadorEs256(None)
        firma = f.firmar(b"mensaje")
        assert f.verificar(b"mensaje", firma) is True

    def test_rechaza_mensaje_alterado(self) -> None:
        f = FirmadorEs256(None)
        firma = f.firmar(b"mensaje")
        assert f.verificar(b"otro", firma) is False

    def test_rechaza_firma_alterada(self) -> None:
        f = FirmadorEs256(None)
        firma = bytearray(f.firmar(b"mensaje"))
        firma[-1] ^= 1
        assert f.verificar(b"mensaje", bytes(firma)) is False

    def test_kid_estable_por_clave(self) -> None:
        pem = _pem()
        assert FirmadorEs256(pem).kid == FirmadorEs256(pem).kid
        assert len(FirmadorEs256(pem).kid) == 16

    def test_pem_invalido(self) -> None:
        with pytest.raises(FirmaInvalida):
            FirmadorEs256(b"esto no es una clave pem")


class TestFirmaUseCase:
    async def test_firmar_devuelve_evidencia(self) -> None:
        uc, store = _uc()
        res = await uc.firmar_async("transaccion", "t1", {"cuenta": "123", "monto": 9}, "42")
        assert res.alg == "ES256"
        assert res.evidencia_id
        assert res.valor_firma
        assert len(res.hash_payload) == 64
        guardada = await store.obtener(res.evidencia_id)
        assert guardada is not None
        assert guardada.emisor == "42"

    async def test_verificar_firma_valida(self) -> None:
        uc, _store = _uc()
        payload = {"cuenta": "123", "monto": 9}
        res = await uc.firmar_async("transaccion", "t1", payload, "42")
        out = await uc.verificar_async(payload, res.valor_firma)
        assert out.valida is True
        assert out.alg == "ES256"

    async def test_verificar_payload_alterado(self) -> None:
        uc, _store = _uc()
        res = await uc.firmar_async("transaccion", "t1", {"monto": 9}, "42")
        out = await uc.verificar_async({"monto": 10}, res.valor_firma)
        assert out.valida is False

    async def test_verificar_firma_basura(self) -> None:
        uc, _store = _uc()
        out = await uc.verificar_async({"a": 1}, "no-es-base64-valida-!!!")
        assert out.valida is False

    async def test_cadena_tamper_evident(self) -> None:
        uc, store = _uc()
        res1 = await uc.firmar_async("transaccion", "t1", {"n": 1}, "42")
        res2 = await uc.firmar_async("transaccion", "t2", {"n": 2}, "42")
        ev2 = await store.obtener(res2.evidencia_id)
        assert ev2 is not None
        assert ev2.hash_anterior == res1.hash_evidencia
        assert ev2.hash_evidencia != res1.hash_evidencia


def _mini_app(uc) -> FastAPI:
    mini = FastAPI()
    mini.include_router(firma_router.router, prefix=SL + "api" + SL + "v1" + SL + "firmas")
    mini.dependency_overrides[get_authorization_service] = _authz_off
    mini.dependency_overrides[require_token] = lambda: {"sub": "42"}
    mini.dependency_overrides[get_firma_digital_uc] = lambda: uc
    return mini


class TestEndpoints:
    def test_firmar_y_verificar_por_http(self) -> None:
        uc, _store = _uc()
        cliente = TestClient(_mini_app(uc))
        base = SL + "api" + SL + "v1" + SL + "firmas"
        r1 = cliente.post(
            base,
            json={"recurso_tipo": "transaccion", "recurso_id": "t1", "payload": {"c": "1"}},
        )
        assert r1.status_code == 201
        firma = r1.json()["valor_firma"]
        r2 = cliente.post(
            base + SL + "verificar", json={"payload": {"c": "1"}, "valor_firma": firma}
        )
        assert r2.status_code == 200
        assert r2.json()["valida"] is True


def test_app_real_registra_firma_router() -> None:
    rutas = [getattr(r, "path", "") for r in app_real.routes]
    assert any("firmas" in ruta for ruta in rutas)

class TestAutorizacionAp0053F6:
    """AP-0053 F6: la firma digital es autoservicio (emisor=token.sub); un
    comisionista debe poder firmar y verificar sus propios recursos sin permiso de
    staff (regresion corregida: F3 la habia gateado por error con FIRMA_GESTIONAR,
    que solo tienen webmaster y staff)."""

    def test_comisionista_puede_firmar_su_propio_recurso(self) -> None:
        uc, _store = _uc()
        mini = FastAPI()
        mini.include_router(firma_router.router, prefix=SL + "api" + SL + "v1" + SL + "firmas")
        mini.dependency_overrides[get_authorization_service] = _authz_off
        mini.dependency_overrides[require_token] = (
            lambda: {"sub": "42", "roles": ["comisionista"]}
        )
        mini.dependency_overrides[get_firma_digital_uc] = lambda: uc
        resp = TestClient(mini).post(
            SL + "api" + SL + "v1" + SL + "firmas",
            json={"recurso_tipo": "transaccion", "recurso_id": "t1", "payload": {"c": "1"}},
        )
        assert resp.status_code == 201

    def test_sin_token_401(self) -> None:
        mini = FastAPI()
        mini.include_router(firma_router.router, prefix=SL + "api" + SL + "v1" + SL + "firmas")
        mini.dependency_overrides[get_authorization_service] = _authz_off
        resp = TestClient(mini).post(
            SL + "api" + SL + "v1" + SL + "firmas",
            json={"recurso_tipo": "transaccion", "recurso_id": "t1", "payload": {"c": "1"}},
        )
        assert resp.status_code == 401
