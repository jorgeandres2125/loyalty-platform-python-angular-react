from __future__ import annotations

from src.domain.services.politica_sesiones import PoliticaSesiones

_ROLES_CANAL = frozenset({"comisionista", "ejecutivo"})


def _politica(max_canal: int = 0, max_otras: int = 0) -> PoliticaSesiones:
    return PoliticaSesiones(
        max_canal=max_canal, max_otras=max_otras, roles_canal=_ROLES_CANAL
    )


def test_rol_de_canal_se_detecta() -> None:
    p = _politica()
    assert p.es_canal(["comisionista"]) is True
    assert p.es_canal(["administrator"]) is False


def test_max_ilimitado_por_defecto_modo_informar() -> None:
    p = _politica(max_canal=0, max_otras=0)
    assert p.max_sesiones(["comisionista"]) == 0
    assert p.max_sesiones(["administrator"]) == 0


def test_max_configurable_por_canal_y_otras() -> None:
    p = _politica(max_canal=1, max_otras=3)
    assert p.max_sesiones(["comisionista"]) == 1
    assert p.max_sesiones(["administrator"]) == 3


def test_mezcla_de_roles_prioriza_canal() -> None:
    p = _politica(max_canal=1, max_otras=3)
    assert p.max_sesiones(["administrator", "ejecutivo"]) == 1
