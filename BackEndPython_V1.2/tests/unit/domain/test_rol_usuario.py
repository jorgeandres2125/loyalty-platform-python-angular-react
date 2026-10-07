import pytest

from src.domain.value_objects.rol_usuario import RolUsuario


def test_catorce_roles_definidos():
    roles = list(RolUsuario)
    assert len(roles) == 14


def test_desde_legacy_comisionista_consumo():
    rol = RolUsuario.desde_legacy("comisionista consumo")
    assert rol == RolUsuario.COMISIONISTA_CONSUMO


def test_desde_legacy_ejecutivo_movilidad_consumo():
    rol = RolUsuario.desde_legacy("ejecutivo movilidad-consumo")
    assert rol == RolUsuario.EJECUTIVO_MOVILIDAD_CONSUMO


def test_desde_legacy_desconocido_lanza_error():
    with pytest.raises(ValueError):
        RolUsuario.desde_legacy("rol inexistente")
