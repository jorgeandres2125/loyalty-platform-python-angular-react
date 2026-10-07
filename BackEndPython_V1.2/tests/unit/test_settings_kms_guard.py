from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.infrastructure.config.settings import Settings


def _prod_base(**ov: object) -> dict[str, object]:
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


class TestKmsGuard:
    def test_prod_local_rechazado(self) -> None:
        with pytest.raises(ValidationError):
            Settings(app_env="production", **_prod_base(kms_provider="local"))

    def test_staging_local_rechazado(self) -> None:
        with pytest.raises(ValidationError):
            Settings(app_env="staging", **_prod_base(kms_provider="local"))

    def test_prod_aws_sin_key_id_rechazado(self) -> None:
        with pytest.raises(ValidationError):
            Settings(app_env="production", **_prod_base(kms_key_id=""))

    def test_proveedor_invalido_rechazado(self) -> None:
        with pytest.raises(ValidationError):
            Settings(app_env="development", kms_provider="hsm-x")

    def test_prod_aws_valido(self) -> None:
        s = Settings(app_env="production", **_prod_base())
        assert s.kms_provider == "aws"

    def test_dev_local_valido(self) -> None:
        s = Settings(app_env="development", kms_provider="local")
        assert s.kms_provider == "local"
