"""Tests para LoginUseCase (orquesta autenticación + retraso incremental AP-0007)."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.services.login_throttle_service import LoginThrottleService
from src.application.use_cases.login_use_case import LoginUseCase
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.credenciales_invalidas import CredencialesInvalidas
from src.infrastructure.external.in_memory_intentos_login_store import InMemoryIntentosLoginStore


def _usuario(uid: int = 1) -> UsuarioEntity:
    return UsuarioEntity(uid=uid, nombre=str(uid), email="x@y.co", roles=[], activo=True)


def _build(
    autenticar_return=None,
    autenticar_side_effect=None,
) -> tuple[LoginUseCase, list[float]]:
    auth = AsyncMock()
    if autenticar_side_effect is not None:
        auth.autenticar_async.side_effect = autenticar_side_effect
    else:
        auth.autenticar_async.return_value = autenticar_return
    # generar_token es síncrono → MagicMock, no AsyncMock.
    auth.generar_token = MagicMock(return_value="tok")

    throttle = LoginThrottleService(
        store=InMemoryIntentosLoginStore(ttl_segundos=900),
        paso_segundos=5,
        maximo_segundos=30,
    )
    modulos_repo = AsyncMock()
    modulos_repo.obtener_modulos_por_uid_async.return_value = []

    dormido: list[float] = []

    async def fake_sleep(segundos: float) -> None:
        dormido.append(segundos)

    sleeper: Callable[[float], Awaitable[None]] = fake_sleep
    uc = LoginUseCase(
        auth_service=auth,
        throttle=throttle,
        usuario_repo=AsyncMock(),
        modulos_repo=modulos_repo,
        sleeper=sleeper,
    )
    return uc, dormido


@pytest.mark.asyncio
async def test_login_exitoso_retorna_resultado_sin_dormir() -> None:
    uc, dormido = _build(autenticar_return=_usuario(7))
    result = await uc.ejecutar_async("7", "pw", "ip|7")
    assert result.token == "tok"
    assert result.usuario.uid == 7
    assert result.modulos == []
    assert dormido == []  # un login válido nunca aplica retraso


@pytest.mark.asyncio
async def test_credenciales_invalidas_lanza_y_duerme_5() -> None:
    uc, dormido = _build(autenticar_return=None)
    with pytest.raises(CredencialesInvalidas):
        await uc.ejecutar_async("1", "bad", "ip|1")
    assert dormido == [5]


@pytest.mark.asyncio
async def test_fallos_consecutivos_incrementan_la_espera() -> None:
    uc, dormido = _build(autenticar_return=None)
    for _ in range(3):
        with pytest.raises(CredencialesInvalidas):
            await uc.ejecutar_async("1", "bad", "ip|1")
    assert dormido == [5, 10, 15]


@pytest.mark.asyncio
async def test_exito_reinicia_la_curva_de_retraso() -> None:
    # falla, falla, acierta (reset), falla → la espera vuelve a 5.
    uc, dormido = _build(autenticar_side_effect=[None, None, _usuario(), None])
    with pytest.raises(CredencialesInvalidas):
        await uc.ejecutar_async("1", "b", "k")
    with pytest.raises(CredencialesInvalidas):
        await uc.ejecutar_async("1", "b", "k")
    await uc.ejecutar_async("1", "ok", "k")  # éxito → reinicia el contador
    with pytest.raises(CredencialesInvalidas):
        await uc.ejecutar_async("1", "b", "k")
    assert dormido == [5, 10, 5]
