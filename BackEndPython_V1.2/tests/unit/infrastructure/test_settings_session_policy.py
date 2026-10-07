from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.infrastructure.config.settings import Settings
from src.shared.constants.password_policy import PASSWORD_MIN_LONGITUD_USUARIO_SERVICIO
from src.shared.constants.session_policy import (
    JWT_EXPIRE_MINUTES_DEFECTO,
    JWT_EXPIRE_MINUTES_MAXIMO,
)


def _base(**overrides: object) -> dict[str, object]:
    larga: str = "x" * PASSWORD_MIN_LONGITUD_USUARIO_SERVICIO
    base: dict[str, object] = {
        "jwt_secret_key": larga,
        "db_user": "app_sufi",
        "db_password": larga,
        "smtp_password": "",
        "email_api_password": "",
    }
    base.update(overrides)
    return base


class TestSessionTimeoutPolicy:
    """AP-0162: timeout absoluto de sesion."""

    def test_defecto_es_30_minutos(self) -> None:
        s = Settings(app_env="development", **_base())
        assert s.jwt_expire_minutes == JWT_EXPIRE_MINUTES_DEFECTO
        assert s.jwt_expire_minutes == 30

    def test_maximo_es_480_minutos(self) -> None:
        assert JWT_EXPIRE_MINUTES_MAXIMO == 480

    def test_acepta_valor_dentro_del_rango(self) -> None:
        s = Settings(app_env="development", **_base(jwt_expire_minutes=60))
        assert s.jwt_expire_minutes == 60

    def test_rechaza_valor_mayor_al_maximo(self) -> None:
        with pytest.raises(ValidationError):
            Settings(
                app_env="production",
                **_base(jwt_expire_minutes=JWT_EXPIRE_MINUTES_MAXIMO + 1),
            )

    def test_rechaza_valor_menor_al_minimo(self) -> None:
        with pytest.raises(ValidationError):
            Settings(
                app_env="development",
                **_base(jwt_expire_minutes=4),
            )
