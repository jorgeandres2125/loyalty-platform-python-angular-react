from __future__ import annotations

import time

from src.application.services.auth_service import AuthService
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.services.politica_inactividad import PoliticaInactividad
from src.domain.value_objects.rol_usuario import RolUsuario
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import PasswordHasher

_SEG_CANAL = 420
_SEG_OTRAS = 1200
_SEG_ABS = 1800


def _svc() -> AuthService:
    return AuthService(
        jwt_handler=JWTHandler("test-secret-key-min-32-chars-xxxxx", "HS256"),
        password_hasher=PasswordHasher(),
        jwt_expire_minutes=30,
        politica_inactividad=PoliticaInactividad(
            minutos_canal=7, minutos_otras=20, roles_canal=frozenset({"comisionista"})
        ),
    )


def _usuario(roles: list[RolUsuario]) -> UsuarioEntity:
    return UsuarioEntity(
        uid=1,
        nombre="1",
        email="x@y.co",
        roles=roles,
        activo=True,
        new_pass_hash=PasswordHasher().hashear("Admin2024*"),
    )


def test_token_de_canal_expira_por_inactividad_en_7_min() -> None:
    svc = _svc()
    payload = svc.verificar_token(svc.generar_token(_usuario([RolUsuario.COMISIONISTA])))
    assert payload["canal"] is True
    vida = int(payload["exp"]) - int(payload["auth_epoch"])
    assert abs(vida - _SEG_CANAL) <= 2
    assert int(payload["abs_exp"]) - int(payload["auth_epoch"]) == _SEG_ABS


def test_token_de_otra_app_expira_por_inactividad_en_20_min() -> None:
    svc = _svc()
    payload = svc.verificar_token(svc.generar_token(_usuario([RolUsuario.ADMINISTRATOR])))
    assert payload["canal"] is False
    vida = int(payload["exp"]) - int(payload["auth_epoch"])
    assert abs(vida - _SEG_OTRAS) <= 2


def test_renovar_preserva_abs_exp_y_desliza_inactividad() -> None:
    svc = _svc()
    ahora = int(time.time())
    abs_exp = ahora + _SEG_ABS
    claims = {
        "sub": "1",
        "nombre": "1",
        "roles": ["comisionista"],
        "tv": 3,
        "auth_epoch": ahora,
        "amr": ["pwd"],
        "abs_exp": abs_exp,
        "canal": True,
    }
    payload = svc.verificar_token(svc.renovar_token(claims))
    assert int(payload["abs_exp"]) == abs_exp
    assert payload["tv"] == 3
    assert abs((int(payload["exp"]) - ahora) - _SEG_CANAL) <= 3


def test_sin_politica_conserva_comportamiento_previo() -> None:
    svc = AuthService(
        jwt_handler=JWTHandler("test-secret-key-min-32-chars-xxxxx", "HS256"),
        password_hasher=PasswordHasher(),
        jwt_expire_minutes=30,
    )
    payload = svc.verificar_token(svc.generar_token(_usuario([RolUsuario.COMISIONISTA])))
    assert "canal" not in payload
    assert "abs_exp" not in payload
