"""Utilidades compartidas para los scripts de migración sufiatulado -> sufi_db.

Construye una URL SQLAlchemy *síncrona* (pyodbc) a partir de los Settings del
backend, para no duplicar ni hardcodear credenciales. Los scripts de migración
son operativos (one-shot), por eso usan el driver síncrono en vez del async.
"""
from __future__ import annotations

from typing import Final

from sqlalchemy import Engine, create_engine

from src.infrastructure.config.settings import Settings

SOURCE_DB: Final[str] = "sufiatulado"
TARGET_DB: Final[str] = "sufi_db"


def sync_engine(db_name: str, *, echo: bool = False, fast_executemany: bool = False) -> Engine:
    """Engine síncrono (mssql+pyodbc) apuntando a `db_name` en el mismo servidor.

    `fast_executemany=True` agrupa los parámetros de executemany en pocas idas y
    vueltas (acelera mucho INSERT/UPDATE masivos); útil para backfills.
    """
    settings: Settings = Settings()
    driver: str = settings.db_driver.replace(" ", "+")
    url: str = (
        f"mssql+pyodbc://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{db_name}"
        f"?driver={driver}&TrustServerCertificate=yes"
    )
    return create_engine(url, echo=echo, future=True, fast_executemany=fast_executemany)
