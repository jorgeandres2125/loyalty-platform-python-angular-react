"""Tests para VerificarEmailUseCase (AP-0004: verificación de propiedad del correo).

Cubre el doble opt-in completo sin BD: perfil_repo, codigo_store, notificador e
historico_repo se sustituyen por AsyncMock.
"""
from __future__ import annotations

import hashlib
from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.verificar_email_use_case import VerificarEmailUseCase
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.exceptions.codigo_invalido import CodigoInvalido
from src.domain.value_objects.codigo_verificacion import CodigoVerificacion


def _hash(codigo: str) -> str:
    return hashlib.sha256(codigo.encode("utf-8")).hexdigest()


def _reg(codigo: str, intentos: int = 5, creado: float = 1000.0) -> CodigoVerificacion:
    return CodigoVerificacion(
        codigo_hash=_hash(codigo), intentos_restantes=intentos, creado_en_monotonic=creado
    )


def _perfil(
    numero_documento: str = "1129565843",
    tipo_documento: str = "C.C.",
    email: str | None = "juan.perez@correo.com",
) -> PerfilContactoEntity:
    return PerfilContactoEntity(
        numero_documento=numero_documento,
        tipo_documento=tipo_documento,
        nombre_completo="Juan Pérez",
        email=email,
    )


def _make_uc(
    perfil: PerfilContactoEntity | None = None,
    registro: CodigoVerificacion | None = None,
    clock_value: float = 1000.0,
    max_intentos: int = 5,
    cooldown_segundos: int = 60,
    frontend_base_url: str = "",
) -> tuple[VerificarEmailUseCase, dict[str, AsyncMock]]:
    perfil_repo = AsyncMock()
    perfil_repo.obtener_contacto_async.return_value = perfil
    perfil_repo.marcar_email_verificado_async.return_value = None
    codigo_store = AsyncMock()
    codigo_store.obtener.return_value = registro
    notificador = AsyncMock()
    historico_repo = AsyncMock()
    uc = VerificarEmailUseCase(
        perfil_repo=perfil_repo,
        codigo_store=codigo_store,
        notificador=notificador,
        historico_repo=historico_repo,
        ttl_horas=24,
        max_intentos=max_intentos,
        cooldown_segundos=cooldown_segundos,
        frontend_base_url=frontend_base_url,
        clock=lambda: clock_value,
    )
    return uc, {
        "perfil_repo": perfil_repo,
        "codigo_store": codigo_store,
        "notificador": notificador,
        "historico_repo": historico_repo,
    }


# ── solicitar: happy path ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_solicitar_envia_codigo_y_registra_historico() -> None:
    uc, m = _make_uc(perfil=_perfil(), registro=None)
    res = await uc.solicitar_codigo_async("C.C.", "1129565843")
    assert res.enviado is True
    assert res.email_enmascarado == "j***@correo.com"
    assert res.expira_en_horas == 24
    m["codigo_store"].guardar.assert_awaited_once()
    m["notificador"].enviar_async.assert_awaited_once()
    m["historico_repo"].registrar_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_solicitar_guarda_solo_hash_y_codigo_de_8_digitos() -> None:
    uc, m = _make_uc(perfil=_perfil(), registro=None)
    await uc.solicitar_codigo_async("C.C.", "1129565843")
    # El código en claro viaja en el correo; el store recibe solo el hash.
    registro_guardado: CodigoVerificacion = m["codigo_store"].guardar.await_args.args[1]
    cuerpo_texto: str = m["notificador"].enviar_async.await_args.kwargs["cuerpo_texto"]
    codigo_enviado: str = next(t for t in cuerpo_texto.split() if t.isdigit() and len(t) == 8)
    assert registro_guardado.codigo_hash == _hash(codigo_enviado)
    assert registro_guardado.codigo_hash != codigo_enviado
    assert registro_guardado.intentos_restantes == 5


@pytest.mark.asyncio
async def test_solicitar_incluye_enlace_cuando_hay_frontend_url() -> None:
    uc, m = _make_uc(
        perfil=_perfil(), registro=None, frontend_base_url="https://app.suficontigo.com/"
    )
    await uc.solicitar_codigo_async("C.C.", "1129565843")
    cuerpo_html: str = m["notificador"].enviar_async.await_args.kwargs["cuerpo_html"]
    cuerpo_texto: str = m["notificador"].enviar_async.await_args.kwargs["cuerpo_texto"]
    # rstrip evita el doble slash: .../verificar-correo, no ...//verificar-correo.
    # El enlace lleva el documento para aterrizar en el paso de ingresar el código;
    # en HTML el '&' va escapado como '&amp;'.
    assert (
        'href="https://app.suficontigo.com/verificar-correo?doc=1129565843&amp;tipo=C.C."'
        in cuerpo_html
    )
    assert "https://app.suficontigo.com/verificar-correo?doc=1129565843&tipo=C.C." in cuerpo_texto


@pytest.mark.asyncio
async def test_solicitar_sin_frontend_url_no_incluye_enlace() -> None:
    uc, m = _make_uc(perfil=_perfil(), registro=None, frontend_base_url="")
    await uc.solicitar_codigo_async("C.C.", "1129565843")
    cuerpo_html: str = m["notificador"].enviar_async.await_args.kwargs["cuerpo_html"]
    assert "verificar-correo" not in cuerpo_html
    assert "<a href" not in cuerpo_html


# ── solicitar: anti-enumeración ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_solicitar_sin_perfil_respuesta_neutra() -> None:
    uc, m = _make_uc(perfil=None)
    res = await uc.solicitar_codigo_async("C.C.", "0000")
    assert res.enviado is False
    assert res.email_enmascarado is None
    m["notificador"].enviar_async.assert_not_awaited()
    m["codigo_store"].guardar.assert_not_awaited()


@pytest.mark.asyncio
async def test_solicitar_perfil_sin_correo_respuesta_neutra() -> None:
    uc, m = _make_uc(perfil=_perfil(email=None))
    res = await uc.solicitar_codigo_async("C.C.", "1129565843")
    assert res.enviado is False
    m["notificador"].enviar_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_solicitar_tipo_documento_no_coincide_respuesta_neutra() -> None:
    uc, m = _make_uc(perfil=_perfil(tipo_documento="C.C."))
    res = await uc.solicitar_codigo_async("C.E.", "1129565843")
    assert res.enviado is False
    m["notificador"].enviar_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_solicitar_tipo_documento_formato_equivalente_coincide() -> None:
    # El dato legado guarda "CC"; el formulario envía "C.C." → deben emparejar.
    uc, m = _make_uc(perfil=_perfil(tipo_documento="CC"))
    res = await uc.solicitar_codigo_async("C.C.", "1129565843")
    assert res.enviado is True
    m["notificador"].enviar_async.assert_awaited_once()


# ── solicitar: cooldown ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_solicitar_en_cooldown_no_reenvia() -> None:
    reciente = _reg("11112222", creado=1000.0)
    uc, m = _make_uc(perfil=_perfil(), registro=reciente, clock_value=1030.0, cooldown_segundos=60)
    res = await uc.solicitar_codigo_async("C.C.", "1129565843")
    assert res.enviado is False
    assert res.en_cooldown is True
    m["notificador"].enviar_async.assert_not_awaited()
    m["codigo_store"].guardar.assert_not_awaited()


@pytest.mark.asyncio
async def test_solicitar_tras_cooldown_reenvia() -> None:
    viejo = _reg("11112222", creado=1000.0)
    uc, m = _make_uc(perfil=_perfil(), registro=viejo, clock_value=1100.0, cooldown_segundos=60)
    res = await uc.solicitar_codigo_async("C.C.", "1129565843")
    assert res.enviado is True
    m["notificador"].enviar_async.assert_awaited_once()


# ── confirmar ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_confirmar_codigo_correcto_marca_verificado() -> None:
    registro = _reg("12345678", intentos=5)
    uc, m = _make_uc(perfil=_perfil(), registro=registro)
    res = await uc.confirmar_codigo_async("C.C.", "1129565843", "12345678")
    assert res.verificado is True
    m["codigo_store"].eliminar.assert_awaited_once()
    m["perfil_repo"].marcar_email_verificado_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_confirmar_sin_codigo_vigente_lanza() -> None:
    uc, _ = _make_uc(registro=None)
    with pytest.raises(CodigoInvalido, match="expiró"):
        await uc.confirmar_codigo_async("C.C.", "1129565843", "12345678")


@pytest.mark.asyncio
async def test_confirmar_codigo_incorrecto_consume_intento() -> None:
    registro = _reg("12345678", intentos=5)
    uc, m = _make_uc(registro=registro)
    with pytest.raises(CodigoInvalido) as exc:
        await uc.confirmar_codigo_async("C.C.", "1129565843", "00000000")
    assert exc.value.intentos_restantes == 4
    m["codigo_store"].guardar.assert_awaited_once()
    m["perfil_repo"].marcar_email_verificado_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_confirmar_agota_intentos_invalida_codigo() -> None:
    registro = _reg("12345678", intentos=1)
    uc, m = _make_uc(registro=registro)
    with pytest.raises(CodigoInvalido) as exc:
        await uc.confirmar_codigo_async("C.C.", "1129565843", "00000000")
    assert exc.value.intentos_restantes == 0
    m["codigo_store"].eliminar.assert_awaited_once()
    m["codigo_store"].guardar.assert_not_awaited()
