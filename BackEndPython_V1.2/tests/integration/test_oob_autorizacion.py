from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.main import app as app_real
from src.adapters.api.routers import oob_router
from src.application.services.authorization_service import AuthorizationService
from src.application.services.ownership_validator import OwnershipValidator
from src.application.services.permission_evaluator import PermissionEvaluator
from src.application.services.servicio_ownership import ServicioOwnership
from src.application.use_cases.autorizacion_oob_use_case import AutorizacionOobUseCase
from src.domain.entities.desafio_oob import DesafioOob
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.desafio_oob_invalido import DesafioOobInvalido
from src.domain.services.clasificador_criticidad import ClasificadorCriticidad
from src.domain.value_objects.canal_oob import CanalOob
from src.domain.value_objects.estado_desafio_oob import EstadoDesafioOob
from src.domain.value_objects.tipo_transaccion_critica import TipoTransaccionCritica
from src.infrastructure.config.dependencies import (
    get_authorization_service,
    get_autorizacion_oob_uc,
    require_token,
)
from src.infrastructure.external.in_memory_desafio_oob_store import InMemoryDesafioOobStore

SL = chr(47)
NL = chr(10)


class FakeUsuarioRepo:
    def __init__(self, usuario: UsuarioEntity | None) -> None:
        self._usuario = usuario

    async def obtener_por_uid_async(self, uid: int) -> UsuarioEntity | None:
        return self._usuario


class FakeNotificador:
    def __init__(self) -> None:
        self.enviados: list[tuple[str, str, str, str]] = []

    async def enviar_async(self, destinatario, asunto, cuerpo_texto, cuerpo_html) -> None:
        self.enviados.append((destinatario, asunto, cuerpo_texto, cuerpo_html))

    async def enviar_masivo_async(self, destinatarios, asunto, cuerpo_texto, cuerpo_html) -> None:
        self.enviados.append((",".join(destinatarios), asunto, cuerpo_texto, cuerpo_html))


def _usuario() -> UsuarioEntity:
    return UsuarioEntity(uid=42, nombre="Ana", email="ana@example.com")


def _uc(usuario, max_intentos=3, ttl=300):
    store = InMemoryDesafioOobStore(ttl_segundos=ttl)
    notif = FakeNotificador()
    uc = AutorizacionOobUseCase(
        usuario_repo=FakeUsuarioRepo(usuario),
        desafio_store=store,
        notificador=notif,
        clasificador=ClasificadorCriticidad(),
        max_intentos=max_intentos,
        ttl_segundos=ttl,
    )
    return uc, store, notif


def _codigo_de(notif: FakeNotificador) -> str:
    for linea in notif.enviados[-1][2].split(NL):
        if linea.isdigit() and len(linea) == 6:
            return linea
    raise AssertionError("no se encontro codigo en el correo")


def _desafio(estado=EstadoDesafioOob.PENDIENTE, intentos=3) -> DesafioOob:
    return DesafioOob(
        desafio_id="d1",
        uid="42",
        tipo_transaccion=TipoTransaccionCritica.CAMBIO_CUENTA_BANCARIA,
        canal=CanalOob.CORREO,
        payload_hash="h",
        codigo_hash="c",
        intentos_restantes=intentos,
        creado_en_monotonic=0.0,
        estado=estado,
    )


class TestDesafioOob:
    def test_transiciones(self) -> None:
        d = _desafio()
        assert d.es_resoluble is True
        assert d.aprobado().estado is EstadoDesafioOob.APROBADA
        assert d.rechazado().estado is EstadoDesafioOob.RECHAZADA
        assert d.bloqueado().estado is EstadoDesafioOob.BLOQUEADA
        assert d.con_intento_consumido().intentos_restantes == 2
        assert _desafio(estado=EstadoDesafioOob.APROBADA).es_resoluble is False


class TestClasificador:
    def test_tipo_conocido_requiere_oob(self) -> None:
        clf = ClasificadorCriticidad()
        tipo = clf.tipo_desde("cambio_cuenta_bancaria")
        assert tipo is TipoTransaccionCritica.CAMBIO_CUENTA_BANCARIA
        assert clf.requiere_oob(tipo) is True

    def test_tipo_desconocido_no_requiere_oob(self) -> None:
        clf = ClasificadorCriticidad()
        assert clf.tipo_desde("consulta_saldo") is None
        assert clf.requiere_oob(None) is False


class TestIniciar:
    async def test_critica_envia_y_crea_desafio(self) -> None:
        uc, store, notif = _uc(_usuario())
        res = await uc.iniciar_async("42", "cambio_cuenta_bancaria", {"cuenta": "123"})
        assert res.requiere_oob is True
        assert res.enviado is True
        assert res.desafio_id is not None
        assert res.estado == EstadoDesafioOob.PENDIENTE.value
        assert res.email_enmascarado == "a***@example.com"
        assert len(notif.enviados) == 1
        guardado = await store.obtener(res.desafio_id)
        assert guardado is not None
        assert guardado.estado is EstadoDesafioOob.PENDIENTE

    async def test_sin_correo_no_envia(self) -> None:
        uc, _store, notif = _uc(UsuarioEntity(uid=42, nombre="X", email=""))
        res = await uc.iniciar_async("42", "cambio_cuenta_bancaria", {})
        assert res.requiere_oob is True
        assert res.enviado is False
        assert notif.enviados == []

    async def test_usuario_inexistente_no_envia(self) -> None:
        uc, _store, _notif = _uc(None)
        res = await uc.iniciar_async("99", "cambio_correo", {})
        assert res.enviado is False


class TestResolver:
    async def test_aprobar_con_codigo_correcto(self) -> None:
        uc, _store, notif = _uc(_usuario())
        res = await uc.iniciar_async("42", "cambio_cuenta_bancaria", {"cuenta": "9"})
        codigo = _codigo_de(notif)
        out = await uc.resolver_async(res.desafio_id, "42", aprobar=True, codigo=codigo)
        assert out.aprobado is True
        assert out.estado == EstadoDesafioOob.APROBADA.value
        assert out.tipo_transaccion == "cambio_cuenta_bancaria"
        assert out.payload_hash is not None

    async def test_codigo_incorrecto_consume_intento(self) -> None:
        uc, _store, notif = _uc(_usuario())
        res = await uc.iniciar_async("42", "cambio_cuenta_bancaria", {})
        with pytest.raises(DesafioOobInvalido) as exc:
            await uc.resolver_async(res.desafio_id, "42", aprobar=True, codigo="000000")
        assert exc.value.intentos_restantes == 2

    async def test_bloqueo_por_intentos_agotados(self) -> None:
        uc, _store, notif = _uc(_usuario(), max_intentos=1)
        res = await uc.iniciar_async("42", "cambio_cuenta_bancaria", {})
        with pytest.raises(DesafioOobInvalido) as exc:
            await uc.resolver_async(res.desafio_id, "42", aprobar=True, codigo="000000")
        assert exc.value.intentos_restantes == 0

    async def test_rechazo(self) -> None:
        uc, _store, notif = _uc(_usuario())
        res = await uc.iniciar_async("42", "cambio_cuenta_bancaria", {})
        out = await uc.resolver_async(res.desafio_id, "42", aprobar=False, codigo=None)
        assert out.aprobado is False
        assert out.estado == EstadoDesafioOob.RECHAZADA.value

    async def test_desafio_inexistente(self) -> None:
        uc, _store, _notif = _uc(_usuario())
        with pytest.raises(DesafioOobInvalido):
            await uc.resolver_async("noexiste", "42", aprobar=True, codigo="000000")

    async def test_otro_usuario_no_puede_resolver(self) -> None:
        uc, _store, notif = _uc(_usuario())
        res = await uc.iniciar_async("42", "cambio_cuenta_bancaria", {})
        codigo = _codigo_de(notif)
        with pytest.raises(DesafioOobInvalido):
            await uc.resolver_async(res.desafio_id, "77", aprobar=True, codigo=codigo)

    async def test_no_se_puede_resolver_dos_veces(self) -> None:
        uc, _store, notif = _uc(_usuario())
        res = await uc.iniciar_async("42", "cambio_cuenta_bancaria", {})
        codigo = _codigo_de(notif)
        await uc.resolver_async(res.desafio_id, "42", aprobar=True, codigo=codigo)
        with pytest.raises(DesafioOobInvalido):
            await uc.resolver_async(res.desafio_id, "42", aprobar=True, codigo=codigo)


class _FakeAuditorObjeto:
    async def registrar(self, *args: object, **kwargs: object) -> None:
        return None


def _authz_off() -> AuthorizationService:
    return AuthorizationService(PermissionEvaluator(), None, None, "off")  # type: ignore[arg-type]


def _authz_con_store(store: InMemoryDesafioOobStore, modo: str) -> AuthorizationService:
    validator = OwnershipValidator(
        servicio_ownership=ServicioOwnership(None),  # type: ignore[arg-type]
        desafio_store=store,
    )
    return AuthorizationService(
        PermissionEvaluator(), validator, _FakeAuditorObjeto(), modo  # type: ignore[arg-type]
    )


def _mini_app(uc):
    mini = FastAPI()
    mini.include_router(oob_router.router, prefix=SL + "api" + SL + "v1" + SL + "oob")
    mini.dependency_overrides[require_token] = lambda: {"sub": "42"}
    mini.dependency_overrides[get_authorization_service] = _authz_off
    mini.dependency_overrides[get_autorizacion_oob_uc] = lambda: uc
    return mini


class TestEndpoints:
    def test_iniciar_y_aprobar_por_http(self) -> None:
        uc, _store, notif = _uc(_usuario())
        cliente = TestClient(_mini_app(uc))
        base = SL + "api" + SL + "v1" + SL + "oob" + SL + "desafios"
        r1 = cliente.post(
            base, json={"tipo_transaccion": "cambio_cuenta_bancaria", "payload": {"cuenta": "1"}}
        )
        assert r1.status_code == 201
        cuerpo = r1.json()
        assert cuerpo["requiere_oob"] is True
        assert cuerpo["enviado"] is True
        desafio_id = cuerpo["desafio_id"]
        codigo = _codigo_de(notif)
        r2 = cliente.post(
            base + SL + desafio_id + SL + "resolver", json={"aprobar": True, "codigo": codigo}
        )
        assert r2.status_code == 200
        assert r2.json()["aprobado"] is True

    def test_codigo_mal_formado_da_422(self) -> None:
        uc, _store, _notif = _uc(_usuario())
        cliente = TestClient(_mini_app(uc))
        base = SL + "api" + SL + "v1" + SL + "oob" + SL + "desafios"
        r = cliente.post(base + SL + "x" + SL + "resolver", json={"aprobar": True, "codigo": "12"})
        assert r.status_code == 422


def test_app_real_registra_oob_router() -> None:
    rutas = [getattr(r, "path", "") for r in app_real.routes]
    assert any("oob" in ruta for ruta in rutas)


class TestGateObjetoOob:
    """AP-0055: la autorizacion a nivel de objeto rechaza (404, oculta existencia)
    intentar resolver un desafio OOB que pertenece a OTRO usuario, antes de tocar el
    caso de uso."""

    def test_desafio_de_otro_usuario_da_404(self) -> None:
        store = InMemoryDesafioOobStore(ttl_segundos=3600)
        desafio = DesafioOob(
            desafio_id="d-ajeno",
            uid="999",
            tipo_transaccion=next(iter(TipoTransaccionCritica)),
            canal=CanalOob.CORREO,
            payload_hash="ph",
            codigo_hash="ch",
            intentos_restantes=3,
            creado_en_monotonic=0.0,
            estado=EstadoDesafioOob.PENDIENTE,
        )
        import asyncio

        asyncio.run(store.guardar("d-ajeno", desafio))
        authz = _authz_con_store(store, "enforce")
        mini = FastAPI()
        mini.include_router(oob_router.router, prefix=SL + "api" + SL + "v1" + SL + "oob")
        mini.dependency_overrides[require_token] = (
            lambda: {"sub": "42", "roles": ["comisionista"]}
        )
        mini.dependency_overrides[get_authorization_service] = lambda: authz
        mini.dependency_overrides[get_autorizacion_oob_uc] = lambda: None
        ruta = (
            SL + "api" + SL + "v1" + SL + "oob" + SL + "desafios" + SL + "d-ajeno"
            + SL + "resolver"
        )
        resp = TestClient(mini, raise_server_exceptions=False).post(
            ruta, json={"aprobar": True, "codigo": "12345678"}
        )
        assert resp.status_code == 404
