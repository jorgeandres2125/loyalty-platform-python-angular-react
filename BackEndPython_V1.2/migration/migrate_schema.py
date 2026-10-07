"""Crea el esquema completo (tablas + FKs + índices) en sufi_db.

Ejecuta Base.metadata.create_all sobre la BD destino. Idempotente:
create_all usa checkfirst=True, por lo que vuelve a correr sin error.

Uso:
    .venv/Scripts/python.exe -m migration.migrate_schema
"""
from __future__ import annotations

from sqlalchemy import Engine, inspect

import src.infrastructure.persistence.models  # noqa: F401 — registra todos los modelos
from src.infrastructure.persistence.base import Base
from migration._common import TARGET_DB, sync_engine


def main() -> None:
    engine: Engine = sync_engine(TARGET_DB)
    print(f"Creando esquema en '{TARGET_DB}' ...")
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    tablas: list[str] = sorted(inspector.get_table_names())
    total_fks: int = 0
    total_idx: int = 0
    for tabla in tablas:
        total_fks += len(inspector.get_foreign_keys(tabla))
        total_idx += len(inspector.get_indexes(tabla))

    print(f"OK — {len(tablas)} tablas, {total_fks} FKs, {total_idx} índices.")
    for tabla in tablas:
        print("  -", tabla)
    engine.dispose()


if __name__ == "__main__":
    main()
