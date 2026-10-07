from __future__ import annotations

from datetime import UTC, datetime, timedelta

from src.application.services.servicio_sesiones import ServicioSesiones
from src.domain.services.politica_sesiones import PoliticaSesiones
from src.domain.value_objects.estado_sesion import EstadoSesion
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion
from src.infrastructure.external.in_memory_sesion_repo import InMemorySesionRepo

_ROLES_CANAL = frozenset({"comisionista"})


def _servicio(habilitado: bool = True) -> tuple[ServicioSesiones, InMemorySesionRepo]:
    repo = InMemorySesionRepo()
    politica = PoliticaSesiones(max_canal=0, max_otras=0, roles_canal=_ROLES_CANAL)
    return ServicioSesiones(repo=repo, politica=politica, habilitado=habilitado), repo


async def _registrar(
    servicio: ServicioSesiones, sid: str, uid: int = 1, expira: datetime | None = None
) -> None:
    await servicio.registrar(
        sid=sid,
        uid=uid,
        roles=["comisionista"],
        jti=f"jti-{sid}",
        device_fp="fp",
        ip="127.0.0.1",
        user_agent="pytest",
        fecha_expiracion=expira,
    )


async def test_cerrar_marca_sesion_con_motivo() -> None:
    # AP-0132: cerrar por logout deja la sesion revocada con el motivo LOGOUT.
    servicio, repo = _servicio()
    await _registrar(servicio, "s1")
    await servicio.cerrar("s1", MotivoCierreSesion.LOGOUT)
    sesion = await repo.obtener("s1")
    assert sesion is not None
    assert sesion.estado == EstadoSesion.REVOCADA
    assert sesion.motivo_cierre == MotivoCierreSesion.LOGOUT
    assert sesion.fecha_cierre is not None
    assert await servicio.esta_revocada("s1") is True


async def test_cerrar_deshabilitado_no_hace_nada() -> None:
    servicio, repo = _servicio(habilitado=False)
    await servicio.cerrar("s1", MotivoCierreSesion.LOGOUT)
    assert await repo.obtener("s1") is None


async def test_cerrar_todas_cierra_todas_las_del_usuario() -> None:
    # AP-0132: revocacion administrativa / cambio de credencial cierra todas.
    servicio, repo = _servicio()
    await _registrar(servicio, "s1", uid=1)
    await _registrar(servicio, "s2", uid=1)
    await _registrar(servicio, "s3", uid=2)
    cerradas = await servicio.cerrar_todas(1, MotivoCierreSesion.REVOCACION_ADMIN)
    assert cerradas == 2
    assert await servicio.esta_revocada("s1") is True
    assert await servicio.esta_revocada("s2") is True
    assert await servicio.esta_revocada("s3") is False
    s1 = await repo.obtener("s1")
    assert s1 is not None
    assert s1.motivo_cierre == MotivoCierreSesion.REVOCACION_ADMIN


async def test_marcar_expiradas_transiciona_las_vencidas() -> None:
    # AP-0132: expiracion automatica -> estado EXPIRADA con fecha efectiva.
    servicio, repo = _servicio()
    ya_vencio = datetime.now(UTC) - timedelta(minutes=1)
    vigente = datetime.now(UTC) + timedelta(hours=8)
    await _registrar(servicio, "vieja", uid=1, expira=ya_vencio)
    await _registrar(servicio, "nueva", uid=1, expira=vigente)
    marcadas = await servicio.marcar_expiradas(1)
    assert marcadas == 1
    vieja = await repo.obtener("vieja")
    assert vieja is not None
    assert vieja.estado == EstadoSesion.EXPIRADA
    assert vieja.motivo_cierre == MotivoCierreSesion.EXPIRACION
    assert vieja.fecha_cierre == ya_vencio
    assert await servicio.esta_revocada("nueva") is False


async def test_listar_barre_expiradas_antes_de_informar() -> None:
    # AP-0132: listar aplica el barrido perezoso; una sesion vencida no se informa activa.
    servicio, _ = _servicio()
    ya_vencio = datetime.now(UTC) - timedelta(minutes=1)
    await _registrar(servicio, "vieja", uid=1, expira=ya_vencio)
    await _registrar(servicio, "viva", uid=1, expira=datetime.now(UTC) + timedelta(hours=8))
    activas = await servicio.listar(1)
    assert {s.sid for s in activas} == {"viva"}