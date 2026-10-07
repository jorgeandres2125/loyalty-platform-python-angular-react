from __future__ import annotations

from src.domain.services.politica_inactividad import PoliticaInactividad

_ROLES_CANAL = frozenset({"comisionista", "comisionista consumo", "ejecutivo"})
_P = PoliticaInactividad(minutos_canal=7, minutos_otras=20, roles_canal=_ROLES_CANAL)


def test_rol_de_canal_usa_7_minutos() -> None:
    assert _P.es_canal(["comisionista"]) is True
    assert _P.limite_minutos(["comisionista"]) == 7


def test_rol_no_canal_usa_20_minutos() -> None:
    assert _P.es_canal(["administrator"]) is False
    assert _P.limite_minutos(["administrator"]) == 20


def test_mezcla_de_roles_gana_el_canal() -> None:
    assert _P.es_canal(["administrator", "ejecutivo"]) is True
    assert _P.limite_minutos(["administrator", "ejecutivo"]) == 7


def test_sin_roles_usa_20_minutos() -> None:
    assert _P.es_canal([]) is False
    assert _P.limite_minutos([]) == 20
