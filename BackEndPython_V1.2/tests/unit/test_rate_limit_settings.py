from __future__ import annotations

from src.infrastructure.config.settings import Settings
from src.shared.constants.rate_limit_policy import (
    RATE_LIMIT_POR_IP_AUTH,
    RATE_LIMIT_POR_IP_DEFECTO,
)


def _base(**overrides: object) -> dict[str, object]:
    defaults: dict[str, object] = {
        "app_env": "development",
        "secret_key": "x" * 32,
        "db_host": "localhost",
        "db_port": 1433,
        "db_name": "sufiatulado",
        "db_user": "app_user",
        "db_password": "pwd",
        "email_api_url": "https://mail.example.com/api",
        "email_api_user": "user@example.com",
        "email_api_password": "password_with_20chars_ok",
        "email_from": "no-reply@example.com",
        "documentos_path": "/tmp",
    }
    defaults.update(overrides)
    return defaults


class TestRateLimitSettings:
    """AP-0166: rate limiting configurable via .env."""

    def test_defecto_habilitado(self) -> None:
        cfg: Settings = Settings(**_base())
        assert cfg.rate_limit_enabled is True

    def test_defecto_limite_defecto(self) -> None:
        cfg: Settings = Settings(**_base())
        assert cfg.rate_limit_por_ip_defecto == RATE_LIMIT_POR_IP_DEFECTO

    def test_defecto_limite_auth(self) -> None:
        cfg: Settings = Settings(**_base())
        assert cfg.rate_limit_por_ip_auth == RATE_LIMIT_POR_IP_AUTH

    def test_configurable_limite_defecto(self) -> None:
        cfg: Settings = Settings(**_base(rate_limit_por_ip_defecto="50/minute"))
        assert cfg.rate_limit_por_ip_defecto == "50/minute"

    def test_configurable_deshabilitado(self) -> None:
        cfg: Settings = Settings(**_base(rate_limit_enabled=False))
        assert cfg.rate_limit_enabled is False
