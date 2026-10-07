"""AP-0044: el validador de Settings exige ≥20 caracteres en credenciales de servicio."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.infrastructure.config.settings import Settings
from src.shared.constants.password_policy import PASSWORD_MIN_LONGITUD_USUARIO_SERVICIO


def _kwargs_base(**overrides: object) -> dict[str, object]:
    """Credenciales de servicio largas (válidas) por defecto; se sobreescriben en cada test."""
    larga: str = "x" * PASSWORD_MIN_LONGITUD_USUARIO_SERVICIO
    base: dict[str, object] = {
        "jwt_secret_key": larga,
        "db_user": "app_sufi",
        "db_password": larga,
        "smtp_password": "",
        "email_api_password": "",
        "kms_provider": "aws",
        "kms_key_id": "kms-test-key-id",
    }
    base.update(overrides)
    return base


def test_servicio_exige_20_caracteres() -> None:
    assert PASSWORD_MIN_LONGITUD_USUARIO_SERVICIO == 20


def test_produccion_rechaza_credencial_de_servicio_corta() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", **_kwargs_base(db_password="corta"))  # type: ignore[arg-type]


def test_staging_rechaza_credencial_de_servicio_corta() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="staging", **_kwargs_base(jwt_secret_key="corta"))  # type: ignore[arg-type]


def test_produccion_acepta_credenciales_largas() -> None:
    s = Settings(app_env="production", **_kwargs_base())  # type: ignore[arg-type]
    assert s.app_env == "production"


def test_produccion_ignora_credencial_vacia_integracion_deshabilitada() -> None:
    """Una credencial vacía = integración deshabilitada; no se valida su longitud."""
    s = Settings(app_env="production", **_kwargs_base(smtp_password=""))  # type: ignore[arg-type]
    assert s.smtp_password == ""


def test_desarrollo_no_aplica_la_politica() -> None:
    """Los defaults de dev son intencionadamente débiles y no deben romper el arranque."""
    s = Settings(app_env="development", **_kwargs_base(db_password="Admin123*"))  # type: ignore[arg-type]
    assert s.app_env == "development"
