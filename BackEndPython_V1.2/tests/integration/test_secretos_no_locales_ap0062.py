"""AP-0062 -- guard anti-secretos locales.

Verifica que las plantillas de entorno de staging y produccion (unicos .env versionados) NO
contengan credenciales privilegiadas en claro: cada campo cifrable esta vacio, es un marcador
enc:gcm: o un placeholder. Y que el usuario de BD no sea una cuenta privilegiada. Es la
evidencia de eliminacion de almacenamiento local y un guard anti-regresion.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.shared.constants.cifrado_config import (
    CAMPOS_CREDENCIALES_CIFRABLES,
    ENC_PREFIJO_CONFIG,
)

_RAIZ: Path = Path(__file__).resolve().parents[2]
_PLANTILLAS: tuple[str, ...] = (".env.staging.example", ".env.production.example")
_USUARIOS_PRIVILEGIADOS: frozenset[str] = frozenset(
    {"sa", "root", "admin", "sysadmin", "dbo", "administrator"}
)
_MARCAS_PLACEHOLDER: tuple[str, ...] = (
    "<",
    "cambie",
    "change",
    "replace",
    "example",
    "your-",
    "prod-db",
)
_CIFRABLES_LOWER: frozenset[str] = frozenset(c.lower() for c in CAMPOS_CREDENCIALES_CIFRABLES)


def _campos_env(texto: str) -> dict[str, str]:
    campos: dict[str, str] = {}
    for linea in texto.splitlines():
        s: str = linea.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        clave, _, valor = s.partition("=")
        campos[clave.strip()] = valor.strip()
    return campos


def _es_placeholder(valor: str) -> bool:
    v: str = valor.lower()
    return any(marca in v for marca in _MARCAS_PLACEHOLDER)


@pytest.mark.parametrize("archivo", _PLANTILLAS)
def test_plantilla_sin_credenciales_en_claro(archivo: str) -> None:
    ruta: Path = _RAIZ.joinpath(archivo)
    if not ruta.exists():
        pytest.skip(f"plantilla ausente: {archivo}")
    campos: dict[str, str] = _campos_env(ruta.read_text(encoding="utf-8"))
    for clave, valor in campos.items():
        if clave.lower() in _CIFRABLES_LOWER:
            seguro: bool = (
                valor == ""
                or valor.startswith(ENC_PREFIJO_CONFIG)
                or _es_placeholder(valor)
            )
            assert seguro, f"AP-0062: {clave} contiene un secreto en claro en {archivo}"


@pytest.mark.parametrize("archivo", _PLANTILLAS)
def test_usuario_bd_no_privilegiado(archivo: str) -> None:
    ruta: Path = _RAIZ.joinpath(archivo)
    if not ruta.exists():
        pytest.skip(f"plantilla ausente: {archivo}")
    campos: dict[str, str] = _campos_env(ruta.read_text(encoding="utf-8"))
    usuario: str = campos.get("DB_USER", "").strip().lower()
    ok: bool = (
        usuario == ""
        or _es_placeholder(usuario)
        or usuario not in _USUARIOS_PRIVILEGIADOS
    )
    assert ok, f"AP-0062: DB_USER privilegiado ({usuario}) en {archivo}"
