"""AP-0079: los secretos no se exponen como defaults del codigo y no se admiten
placeholders; en staging y produccion deben estar presentes (no vacios)."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.infrastructure.config.settings import Settings

SECRETO_FUERTE: str = "k7Qe2vN8sR1tWcYbZpLm4Hj6Dg0Af3uX9oI5nB"


def _kwargs(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "jwt_secret_key": SECRETO_FUERTE,
        "db_user": "app_sufi",
        "db_password": SECRETO_FUERTE,
        "smtp_password": "",
        "email_api_password": "",
        "kms_provider": "aws",
        "kms_key_id": "kms-test-key-id",
    }
    base.update(overrides)
    return base


def test_no_hay_secreto_por_defecto_en_el_codigo() -> None:
    assert Settings.model_fields["jwt_secret_key"].default == ""
    assert Settings.model_fields["db_password"].default == ""


def test_rechaza_placeholder_jwt_en_cualquier_ambiente() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="development", **_kwargs(jwt_secret_key="CHANGE-ME-IN-PRODUCTION"))  # type: ignore[arg-type]


def test_produccion_rechaza_jwt_vacio() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", **_kwargs(jwt_secret_key=""))  # type: ignore[arg-type]


def test_produccion_rechaza_db_password_placeholder() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", **_kwargs(db_password="Admin123*"))  # type: ignore[arg-type]


def test_produccion_acepta_secretos_fuertes() -> None:
    cfg = Settings(app_env="production", **_kwargs())  # type: ignore[arg-type]
    assert cfg.app_env == "production"
