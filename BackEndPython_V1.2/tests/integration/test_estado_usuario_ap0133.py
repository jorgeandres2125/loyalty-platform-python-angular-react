"""AP-0133: un usuario inhabilitado, bloqueado o eliminado pierde el acceso de inmediato,
aun con un JWT vigente. La revalidacion ocurre en cada peticion via ValidadorSesion (el
punto de enforcement que require_token invoca)."""
from __future__ import annotations

import pytest

from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.services.validador_sesion import ValidadorSesion
from src.domain.exceptions.cuenta_bloqueada import CuentaBloqueada
from src.domain.exceptions.sesion_invalida import SesionInvalida
from src.domain.value_objects.estado_usuario import EstadoUsuario
from src.infrastructure.external.in_memory_bloqueo_cuenta_repo import InMemoryBloqueoCuentaRepo
from src.infrastructure.external.in_memory_estado_credencial_repo import (
    InMemoryEstadoCredencialRepo,
)
from src.infrastructure.external.in_memory_revocacion_token_store import (
    InMemoryRevocacionTokenStore,
)


class _RepoEstado:
    """Fake del puerto UsuarioRepository que reporta un estado fijo (AP-0133)."""

    def __init__(self, estado: EstadoUsuario) -> None:
        self._estado: EstadoUsuario = estado

    async def resolver_estado(self, uid: int) -> EstadoUsuario:
        return self._estado


class _BloqueoQueRechaza:
    """AP-0009: simula una cuenta bloqueada por intentos fallidos."""

    async def verificar_no_bloqueada(self, clave: str) -> None:
        raise CuentaBloqueada("cuenta bloqueada")


def _bloqueo_inactivo() -> ServicioBloqueoCuenta:
    return ServicioBloqueoCuenta(
        repo=InMemoryBloqueoCuentaRepo(),
        enabled=False,
        max_intentos=3,
        duracion_minutos=15,
        auto_unlock=True,
        reset_on_success=True,
        count_non_existing=False,
    )


def _validador(usuario_repo: object, bloqueo: object | None = None) -> ValidadorSesion:
    return ValidadorSesion(
        estado_repo=InMemoryEstadoCredencialRepo(),
        denylist=InMemoryRevocacionTokenStore(),
        bloqueo=bloqueo or _bloqueo_inactivo(),  # type: ignore[arg-type]
        usuario_repo=usuario_repo,  # type: ignore[arg-type]
    )


def _claims(uid: int = 7) -> dict[str, object]:
    return {"sub": str(uid), "nombre": "ana", "tv": 1, "jti": "j1"}


async def test_usuario_activo_puede_operar() -> None:
    await _validador(_RepoEstado(EstadoUsuario.ACTIVO)).validar(_claims())


async def test_usuario_inhabilitado_pierde_acceso_inmediato() -> None:
    # AP-0133: JWT vigente pero cuenta inhabilitada -> denegado en la siguiente peticion.
    with pytest.raises(SesionInvalida):
        await _validador(_RepoEstado(EstadoUsuario.INHABILITADO)).validar(_claims())


async def test_usuario_eliminado_pierde_acceso_inmediato() -> None:
    with pytest.raises(SesionInvalida):
        await _validador(_RepoEstado(EstadoUsuario.ELIMINADO)).validar(_claims())


async def test_usuario_bloqueado_pierde_acceso_inmediato() -> None:
    # AP-0133 y AP-0009: cuenta bloqueada -> CuentaBloqueada (require_token la mapea a 403).
    with pytest.raises(CuentaBloqueada):
        await _validador(
            _RepoEstado(EstadoUsuario.ACTIVO), bloqueo=_BloqueoQueRechaza()
        ).validar(_claims())
