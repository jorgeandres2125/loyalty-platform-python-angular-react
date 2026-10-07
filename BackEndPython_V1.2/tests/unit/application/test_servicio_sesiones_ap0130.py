from __future__ import annotations

from src.application.services.servicio_sesiones import ServicioSesiones
from src.domain.entities.sesion_activa_entity import SesionActiva
from src.domain.services.politica_sesiones import PoliticaSesiones
from src.infrastructure.external.in_memory_sesion_repo import InMemorySesionRepo

_ROLES_CANAL = frozenset({"comisionista"})


def _servicio(max_canal: int = 0, max_otras: int = 0, habilitado: bool = True) -> ServicioSesiones:
    politica = PoliticaSesiones(
        max_canal=max_canal, max_otras=max_otras, roles_canal=_ROLES_CANAL
    )
    return ServicioSesiones(repo=InMemorySesionRepo(), politica=politica, habilitado=habilitado)


async def _registrar(servicio: ServicioSesiones, sid: str, uid: int = 1) -> None:
    await servicio.registrar(
        sid=sid,
        uid=uid,
        roles=["comisionista"],
        jti=f"jti-{sid}",
        device_fp="fp",
        ip="127.0.0.1",
        user_agent="pytest",
    )


async def test_modo_informar_no_expulsa_por_defecto() -> None:
    # AP-0130 Opcion A: max en 0 = ilimitado, solo se informa.
    servicio = _servicio(max_canal=0)
    await _registrar(servicio, "s1")
    await _registrar(servicio, "s2")
    await _registrar(servicio, "s3")
    activas: list[SesionActiva] = await servicio.listar(1)
    assert len(activas) == 3


async def test_deshabilitado_no_registra() -> None:
    servicio = _servicio(habilitado=False)
    await _registrar(servicio, "s1")
    assert await servicio.listar(1) == []


async def test_sin_sid_no_registra() -> None:
    servicio = _servicio()
    await servicio.registrar(
        sid="",
        uid=1,
        roles=["comisionista"],
        jti="j1",
        device_fp="fp",
        ip="127.0.0.1",
        user_agent="pytest",
    )
    assert await servicio.listar(1) == []


async def test_control_estricto_expulsa_la_mas_antigua() -> None:
    # AP-0130 Opcion C/D: max=1 -> la sesion previa se expulsa al llegar la nueva.
    servicio = _servicio(max_canal=1)
    await _registrar(servicio, "s1")
    await _registrar(servicio, "s2")
    activas = await servicio.listar(1)
    assert {s.sid for s in activas} == {"s2"}
    assert await servicio.esta_revocada("s1") is True


async def test_control_parametrizable_permite_hasta_el_maximo() -> None:
    servicio = _servicio(max_canal=2)
    await _registrar(servicio, "s1")
    await _registrar(servicio, "s2")
    activas = await servicio.listar(1)
    assert {s.sid for s in activas} == {"s1", "s2"}


async def test_revocar_propia_ok() -> None:
    servicio = _servicio()
    await _registrar(servicio, "s1", uid=1)
    assert await servicio.revocar(uid=1, sid="s1") is True
    assert await servicio.esta_revocada("s1") is True


async def test_revocar_sesion_de_otro_usuario_falla() -> None:
    # AP-0130: no se puede cerrar una sesion que no es propia (ownership).
    servicio = _servicio()
    await _registrar(servicio, "s1", uid=1)
    assert await servicio.revocar(uid=2, sid="s1") is False
    assert await servicio.esta_revocada("s1") is False


async def test_revocar_sesion_inexistente_falla() -> None:
    servicio = _servicio()
    assert await servicio.revocar(uid=1, sid="no-existe") is False


async def test_revocar_otras_deja_solo_la_actual() -> None:
    servicio = _servicio(max_canal=5)
    await _registrar(servicio, "s1", uid=1)
    await _registrar(servicio, "s2", uid=1)
    await _registrar(servicio, "s3", uid=1)
    revocadas = await servicio.revocar_otras(uid=1, sid_actual="s2")
    assert revocadas == 2
    activas = await servicio.listar(1)
    assert {s.sid for s in activas} == {"s2"}


async def test_tocar_actividad_actualiza_last_activity() -> None:
    servicio = _servicio()
    await _registrar(servicio, "s1")
    antes = (await servicio.listar(1))[0].last_activity
    await servicio.tocar_actividad("s1")
    despues = (await servicio.listar(1))[0].last_activity
    assert despues >= antes
