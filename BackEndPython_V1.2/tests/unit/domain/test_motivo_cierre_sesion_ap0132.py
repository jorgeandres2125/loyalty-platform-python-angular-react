from __future__ import annotations

from datetime import UTC, datetime

from src.domain.entities.sesion_activa_entity import SesionActiva
from src.domain.value_objects.estado_sesion import EstadoSesion
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion


def test_motivos_de_cierre_disponibles() -> None:
    # AP-0132: toda terminacion de sesion queda tipificada por un motivo auditable.
    valores = {m.value for m in MotivoCierreSesion}
    assert valores == {
        "logout",
        "expiracion",
        "inactividad",
        "revocacion_admin",
        "limite_concurrencia",
        "cambio_credencial",
    }


def test_sesion_nace_activa_sin_datos_de_cierre() -> None:
    # AP-0132: una sesion recien creada no tiene fecha ni motivo de cierre.
    ahora = datetime.now(UTC)
    sesion = SesionActiva(
        sid="s1",
        uid=1,
        jti_actual="j1",
        device_fp="fp",
        ip="127.0.0.1",
        user_agent="pytest",
        canal=False,
        inicio=ahora,
        last_activity=ahora,
    )
    assert sesion.estado == EstadoSesion.ACTIVA
    assert sesion.fecha_cierre is None
    assert sesion.motivo_cierre is None