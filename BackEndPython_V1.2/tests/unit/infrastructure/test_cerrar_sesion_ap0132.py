from __future__ import annotations

from datetime import UTC, datetime, timedelta

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
        device_fp="fp",
        ip="127.0.0.1",
        user_agent="pytest",
        canal=False,
        inicio=ahora,
        last_activity=ahora,
        fecha_expiracion=ahora + timedelta(hours=8),
    )


async def test_cerrar_registra_estado_motivo_y_fecha() -> None:
    # AP-0132: el cierre deja evidencia: estado terminal + motivo + fecha de cierre.
    repo = InMemorySesionRepo()
    await repo.crear(_sesion())
    momento = datetime.now(UTC)
    await repo.cerrar("s1", EstadoSesion.REVOCADA, MotivoCierreSesion.LOGOUT, momento)
    encontrada = await repo.obtener("s1")
    assert encontrada is not None
    assert encontrada.estado == EstadoSesion.REVOCADA
    assert encontrada.motivo_cierre == MotivoCierreSesion.LOGOUT
    assert encontrada.fecha_cierre == momento


async def test_cerrar_es_idempotente_preserva_primer_motivo() -> None:
    # AP-0132: un segundo cierre no sobreescribe el motivo/fecha del primero.
    repo = InMemorySesionRepo()
    await repo.crear(_sesion())
    primero = datetime.now(UTC)
    await repo.cerrar("s1", EstadoSesion.REVOCADA, MotivoCierreSesion.LOGOUT, primero)
    await repo.cerrar(
        "s1", EstadoSesion.EXPIRADA, MotivoCierreSesion.EXPIRACION, primero + timedelta(minutes=5)
    )
    encontrada = await repo.obtener("s1")
    assert encontrada is not None
    assert encontrada.estado == EstadoSesion.REVOCADA
    assert encontrada.motivo_cierre == MotivoCierreSesion.LOGOUT


async def test_cerrar_sid_inexistente_no_falla() -> None:
    repo = InMemorySesionRepo()
    await repo.cerrar(
        "no-existe", EstadoSesion.REVOCADA, MotivoCierreSesion.LOGOUT, datetime.now(UTC)
    )
    assert await repo.obtener("no-existe") is None