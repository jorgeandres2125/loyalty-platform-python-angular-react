"""AP-0109: opciones por defecto seguras (fail-secure).

1. Defaults de campo seguros (debug off, cookies seguras, CSRF/HSTS on, sin
   confiar en proxy, TLS del gateway verificado, sin usuario de BD ni JWT en codigo).
2. JWT fail-secure: en dev/test una clave vacia se reemplaza por una efimera fuerte.
3. Usuario de BD fail-secure: staging/produccion rechaza ausente/privilegiado/placeholder.
4. Fail-secure no enmascara AP-0079: en produccion una clave JWT vacia sigue fallando.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.infrastructure.config.settings import Settings

_STRONG: str = "xxxxxxxxxxxxxxxxxxxxxxxx"


def _prod_kwargs(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "jwt_secret_key": _STRONG,
        "db_password": _STRONG,
        "db_user": "app_sufi",
        "smtp_password": "",
        "email_api_password": "",
        "kms_provider": "aws",
        "kms_key_id": "kms-test-key-id",
    }
    base.update(overrides)
    return base


# ── 1. Defaults de campo seguros ──────────────────────────────────────────────

def test_defaults_de_campo_seguros() -> None:
    campos = Settings.model_fields
    assert campos["debug"].default is False
    assert campos["cookie_secure"].default is True
    assert campos["csrf_enabled"].default is True
    assert campos["hsts_enabled"].default is True
    assert campos["trust_proxy_headers"].default is False
    assert campos["email_api_verify_tls"].default is True
    assert campos["cors_origin_regex"].default == ""


def test_sin_usuario_bd_ni_jwt_por_defecto_en_codigo() -> None:
    assert Settings.model_fields["db_user"].default == ""
    assert Settings.model_fields["jwt_secret_key"].default == ""


# ── 2. JWT fail-secure (dev/test) ─────────────────────────────────────────────

def test_jwt_vacio_en_dev_genera_clave_efimera() -> None:
    cfg: Settings = Settings(app_env="development", jwt_secret_key="")
    assert cfg.jwt_secret_key != ""
    assert len(cfg.jwt_secret_key) == 64
    assert all(ch in "0123456789abcdef" for ch in cfg.jwt_secret_key)


def test_jwt_vacio_en_test_genera_clave_efimera() -> None:
    cfg: Settings = Settings(app_env="test", jwt_secret_key="")
    assert cfg.jwt_secret_key != ""


def test_jwt_provisto_no_se_reemplaza() -> None:
    cfg: Settings = Settings(app_env="development", jwt_secret_key="mi-clave-fija")
    assert cfg.jwt_secret_key == "mi-clave-fija"


# ── 3. Usuario de BD fail-secure (staging/produccion) ─────────────────────────

def test_produccion_rechaza_db_user_sa() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", **_prod_kwargs(db_user="sa"))  # type: ignore[arg-type]


def test_produccion_rechaza_db_user_vacio() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", **_prod_kwargs(db_user=""))  # type: ignore[arg-type]


def test_produccion_rechaza_placeholder_de_plantilla() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", **_prod_kwargs(db_user="<prod-db-user>"))  # type: ignore[arg-type]


def test_staging_rechaza_db_user_root() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="staging", **_prod_kwargs(db_user="ROOT"))  # type: ignore[arg-type]


def test_produccion_acepta_db_user_de_minimo_privilegio() -> None:
    cfg: Settings = Settings(app_env="production", **_prod_kwargs())  # type: ignore[arg-type]
    assert cfg.db_user == "app_sufi"


def test_desarrollo_no_restringe_db_user() -> None:
    cfg: Settings = Settings(app_env="development", db_user="sa")
    assert cfg.db_user == "sa"


# ── 4. Fail-secure no enmascara AP-0079 ───────────────────────────────────────

def test_produccion_con_jwt_vacio_sigue_fallando() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", **_prod_kwargs(jwt_secret_key=""))  # type: ignore[arg-type]
