"""AP-0092: cifrado de credenciales en el archivo de configuracion.

Cubre el descifrador (roundtrip, marcador, KEK ausente, dato manipulado) y la
integracion con Settings (descifra db_password antes de validar; pasa texto
plano sin cambios; falla si hay valor cifrado sin KEK).
"""
from __future__ import annotations

import base64
import secrets

import pytest
from pydantic import ValidationError

from src.infrastructure.config.secret_decryptor import SecretDecryptor
from src.infrastructure.config.settings import Settings
from src.shared.constants.cifrado_config import ENC_PREFIJO_CONFIG, ENV_CONFIG_KEK

SECRETO_FUERTE: str = "k7Qe2vN8sR1tWcYbZpLm4Hj6Dg0Af3uX9oI5nB"


def _kek() -> bytes:
    return secrets.token_bytes(32)


def test_roundtrip_cifrar_descifrar() -> None:
    dec: SecretDecryptor = SecretDecryptor(_kek())
    enc: str = dec.cifrar_valor(SECRETO_FUERTE)
    assert enc.startswith(ENC_PREFIJO_CONFIG)
    assert dec.descifrar_valor(enc) == SECRETO_FUERTE


def test_valor_sin_marcador_pasa_sin_cambios() -> None:
    dec: SecretDecryptor = SecretDecryptor(_kek())
    assert dec.descifrar_valor("texto-plano") == "texto-plano"
    assert not dec.esta_cifrado("texto-plano")


def test_valor_cifrado_sin_kek_lanza() -> None:
    cifrador: SecretDecryptor = SecretDecryptor(_kek())
    enc: str = cifrador.cifrar_valor(SECRETO_FUERTE)
    sin_kek: SecretDecryptor = SecretDecryptor(None)
    assert not sin_kek.kek_configurada
    with pytest.raises(ValueError):
        sin_kek.descifrar_valor(enc)


def test_kek_incorrecta_lanza() -> None:
    enc: str = SecretDecryptor(_kek()).cifrar_valor(SECRETO_FUERTE)
    otra: SecretDecryptor = SecretDecryptor(_kek())
    with pytest.raises(ValueError):
        otra.descifrar_valor(enc)


def test_base64_invalido_lanza() -> None:
    dec: SecretDecryptor = SecretDecryptor(_kek())
    with pytest.raises(ValueError):
        dec.descifrar_valor(ENC_PREFIJO_CONFIG + "no-es-base64-valido!!!")


def test_kek_longitud_invalida_lanza() -> None:
    with pytest.raises(Exception):
        SecretDecryptor(b"corta")


def test_settings_descifra_db_password(monkeypatch: pytest.MonkeyPatch) -> None:
    kek: bytes = _kek()
    monkeypatch.setenv(ENV_CONFIG_KEK, base64.b64encode(kek).decode("ascii"))
    enc: str = SecretDecryptor(kek).cifrar_valor(SECRETO_FUERTE)
    cfg: Settings = Settings(app_env="development", db_password=enc)
    assert cfg.db_password == SECRETO_FUERTE
    assert SECRETO_FUERTE in cfg.database_url


def test_settings_valor_cifrado_sin_kek_falla(monkeypatch: pytest.MonkeyPatch) -> None:
    kek: bytes = _kek()
    enc: str = SecretDecryptor(kek).cifrar_valor(SECRETO_FUERTE)
    monkeypatch.delenv(ENV_CONFIG_KEK, raising=False)
    with pytest.raises(ValidationError):
        Settings(app_env="development", db_password=enc)


def test_settings_texto_plano_sigue_funcionando(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_CONFIG_KEK, raising=False)
    cfg: Settings = Settings(app_env="development", db_password="plano-dev")
    assert cfg.db_password == "plano-dev"


def test_settings_produccion_con_credenciales_cifradas(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kek: bytes = _kek()
    monkeypatch.setenv(ENV_CONFIG_KEK, base64.b64encode(kek).decode("ascii"))
    cifrador: SecretDecryptor = SecretDecryptor(kek)
    cfg: Settings = Settings(
        app_env="production",
        db_user="app_sufi",
        jwt_secret_key=cifrador.cifrar_valor(SECRETO_FUERTE),
        db_password=cifrador.cifrar_valor(SECRETO_FUERTE),
        smtp_password="",
        email_api_password="",
        kms_provider="aws",
        kms_key_id="kms-test-key-id",
    )
    assert cfg.jwt_secret_key == SECRETO_FUERTE
    assert cfg.db_password == SECRETO_FUERTE
