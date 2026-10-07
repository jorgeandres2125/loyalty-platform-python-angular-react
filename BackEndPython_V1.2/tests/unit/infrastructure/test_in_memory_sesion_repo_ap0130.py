from __future__ import annotations

from datetime import UTC, datetime

from src.domain.entities.sesion_activa_entity import SesionActiva
from src.domain.value_objects.estado_sesion import EstadoSesion
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion
from src.infrastructure.external.in_memory_sesion_repo import InMemorySesionRepo


def _sesion(sid: str = "s1", uid: int = 1) -> SesionActiva:
    ahora = datetime.now(UTC)
    return SesionActiva(
        sid=sid,
        uid=uid,
        jti_actual="j1",
        device_fp="fp1",
        ip="127.0.0.1",
        user_agent="pytest",
        canal=True,
        inicio=ahora,
        last_activity=ahora,
    )


async def _cerrar(repo: InMemorySesionRepo, sid: str) -> None:
    await repo.cerrar(sid, EstadoSesion.REVOCADA, MotivoCierreSesion.LOGOUT, datetime.now(UTC))


async def test_crear_y_obtener() -> None:
    repo = InMemorySesionRepo()
    await repo.crear(_sesion())
    encontrada = await repo.obtener("s1")
    assert encontrada is not None
    assert encontrada.uid == 1


async def test_obtener_inexistente_devuelve_none() -> None:
    repo = InMemorySesionRepo()
    assert await repo.obtener("no-existe") is None


async def test_listar_activas_filtra_por_usuario_y_estado() -> None:
    repo = InMemorySesionRepo()
    await repo.crear(_sesion(sid="s1", uid=1))
    await repo.crear(_sesion(sid="s2", uid=1))
    await repo.crear(_sesion(sid="s3", uid=2))
    await _cerrar(repo, "s2")
    activas = await repo.listar_activas(1)
    assert {s.sid for s in activas} == {"s1"}


async def test_esta_revocada_falso_para_sesion_nueva() -> None:
    repo = InMemorySesionRepo()
    await repo.crear(_sesion())
    assert await repo.esta_revocada("s1") is False


async def test_esta_revocada_verdadero_tras_cerrar() -> None:
    repo = InMemorySesionRepo()
    await repo.crear(_sesion())
    await _cerrar(repo, "s1")
    assert await repo.esta_revocada("s1") is True


async def test_esta_revocada_sid_desconocido_es_falso() -> None:
    # AP-0130: un sid no registrado (config deshabilitada antes, o token viejo) no
    # debe bloquear la peticion; solo se rechaza lo EXPLICITAMENTE revocado.
    repo = InMemorySesionRepo()
    assert await repo.esta_revocada("desconocido") is False


async def test_cerrar_cambia_estado() -> None:
    repo = InMemorySesionRepo()
    await repo.crear(_sesion())
    await _cerrar(repo, "s1")
    encontrada = await repo.obtener("s1")
    assert encontrada is not None
    assert encontrada.estado == EstadoSesion.REVOCADA


async def test_actualizar_actividad() -> None:
    repo = InMemorySesionRepo()
    await repo.crear(_sesion())
    nuevo_momento = datetime.now(UTC)
    await repo.actualizar_actividad("s1", nuevo_momento)
    encontrada = await repo.obtener("s1")
    assert encontrada is not None
    assert encontrada.last_activity == nuevo_momento