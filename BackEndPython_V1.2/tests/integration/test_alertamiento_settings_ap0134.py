"""AP-0134: el alertamiento de eventos de seguridad no puede desactivarse en staging ni
produccion (fail-secure), garantizando que todo evento sensible genere una alerta."""
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


def test_produccion_exige_alertamiento_activo() -> None:
    with pytest.raises(ValueError, match="ALERTAS_SEGURIDAD_ENABLED"):
        Settings(
            app_env="production", alertas_seguridad_enabled=False, **_prod_kwargs()  # type: ignore[arg-type]
        )


def test_staging_exige_alertamiento_activo() -> None:
    with pytest.raises(ValueError, match="ALERTAS_SEGURIDAD_ENABLED"):
        Settings(
            app_env="staging", alertas_seguridad_enabled=False, **_prod_kwargs()  # type: ignore[arg-type]
        )


def test_produccion_por_defecto_alerta() -> None:
    s = Settings(app_env="production", **_prod_kwargs())  # type: ignore[arg-type]
    assert s.alertas_seguridad_enabled is True


def test_desarrollo_permite_desactivar() -> None:
    s = Settings(app_env="development", alertas_seguridad_enabled=False)
    assert s.alertas_seguridad_enabled is False
