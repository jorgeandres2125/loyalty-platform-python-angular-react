"""AP-0061 -- Guard de integracion del minimo privilegio de objetos de BD.

Se conecta a la BD (configurada por variables de entorno) y verifica dos invariantes que la
cuenta de la app puede autoevaluar con minimo privilegio: (1) no posee EXECUTE a nivel de
base de datos (ningun procedimiento o funcion, actual o futuro, es ejecutable por ella) y
(2) no pertenece a roles privilegiados ni de DDL. Es un control anti-regresion: si una
migracion reintroduce el permiso excesivo, el guard falla.

Opt-in: se activa con SUFI_DB_PRIVILEGE_GUARD=1 (lo fija el pipeline de CI tras aprovisionar
la BD efimera). Sin la variable, o sin BD alcanzable, la prueba se omite para no acoplar la
suite local a una BD concreta.
"""
from __future__ import annotations

import asyncio
import os

import pytest
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.infrastructure.persistence.repositories.sql_server_sonda_permisos_objeto import (
    SqlServerSondaPermisosObjeto,
)

_GUARD_ACTIVO: bool = os.getenv("SUFI_DB_PRIVILEGE_GUARD", "").strip().lower() in (
    "1",
    "true",
    "yes",
)

pytestmark = pytest.mark.skipif(
    not _GUARD_ACTIVO,
    reason="Guard de permisos de BD (AP-0061): definir SUFI_DB_PRIVILEGE_GUARD=1 para activar",
)

_ROLES_PRIVILEGIADOS: tuple[str, ...] = (
    "db_owner",
    "db_ddladmin",
    "db_securityadmin",
    "db_accessadmin",
)


def _url() -> URL:
    return URL.create(
        "mssql+aioodbc",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "1433")),
        database=os.getenv("DB_NAME", "sufi_db"),
        query={
            "driver": os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
            "TrustServerCertificate": "yes",
        },
    )


async def _recolectar() -> tuple[list[str], int]:
    engine = create_async_engine(_url())
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        sonda = SqlServerSondaPermisosObjeto(factory)
        anomalias: list[str] = await sonda.anomalias_minimo_privilegio()
        roles_sql: str = "SELECT " + " + ".join(
            f"IS_ROLEMEMBER('{rol}')" for rol in _ROLES_PRIVILEGIADOS
        )
        async with factory() as session:
            en_roles: int = int((await session.execute(text(roles_sql))).scalar() or 0)
        return anomalias, en_roles
    finally:
        await engine.dispose()


def test_app_opera_con_minimo_privilegio_de_objeto() -> None:
    if "DB_USER" not in os.environ or "DB_PASSWORD" not in os.environ:
        pytest.skip("Definir DB_USER y DB_PASSWORD para el guard de BD")
    try:
        anomalias, en_roles = asyncio.run(_recolectar())
    except Exception as exc:  # noqa: BLE001 -- sin BD alcanzable la prueba se omite
        pytest.skip(f"BD no alcanzable para el guard: {exc}")
    assert anomalias == [], f"AP-0061: permisos excesivos de objeto detectados: {anomalias}"
    assert en_roles == 0, "AP-0061: la cuenta de la app pertenece a roles privilegiados o de DDL"
