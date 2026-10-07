"""AP-0133: la revalidacion de sesion por peticion no puede desactivarse en staging ni
produccion (fail-secure). En desarrollo o test si puede apagarse para pruebas."""
from __future__ import annotations

import pytest

from src.infrastructure.config.settings import Settings


def _prod_kwargs(**ov: object) -> dict[str, object]:
    base: dict[str, object] = {
        "jwt_secret_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
        "db_password": "xxxxxxxxxxxxxxxxxxxxxxxx",
        "db_user": "app_sufi",
        "smtp_password": "",
        "email_api_password": "",
        "kms_provider": "aws",
        "kms_key_id": "kms-test-key-id",
    }
    base.update(ov)
    return base


def test_produccion_exige_validacion_activa() -> None:
    with pytest.raises(ValueError, match="SESION_VALIDACION_ENABLED"):
        Settings(
            app_env="production", sesion_validacion_enabled=False, **_prod_kwargs()  # type: ignore[arg-type]
        )


def test_staging_exige_validacion_activa() -> None:
    with pytest.raises(ValueError, match="SESION_VALIDACION_ENABLED"):
        Settings(
            app_env="staging", sesion_validacion_enabled=False, **_prod_kwargs()  # type: ignore[arg-type]
        )


def test_produccion_por_defecto_valida() -> None:
    s = Settings(app_env="production", **_prod_kwargs())  # type: ignore[arg-type]
    assert s.sesion_validacion_enabled is True


def test_desarrollo_permite_desactivar() -> None:
    s = Settings(app_env="development", sesion_validacion_enabled=False)
    assert s.sesion_validacion_enabled is False
