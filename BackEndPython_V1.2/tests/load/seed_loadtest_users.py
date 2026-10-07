"""Siembra / limpieza de usuarios dedicados para la prueba de carga (AP-0031/0032).

Crea N usuarios comisionista (`9_900_000_xxx`) con contraseña bcrypt conocida y su
rol, de modo que el arnés Locust pueda autenticarse y ejercitar lecturas + una
escritura idempotente sobre el PROPIO perfil de cada usuario (sin colisiones →
0 % de errores alcanzable).

Uso (desde la raíz del backend, con el venv activo):

    python tests/load/seed_loadtest_users.py            # siembra
    python tests/load/seed_loadtest_users.py --reset    # limpieza (borra todo lo sembrado)
    python tests/load/seed_loadtest_users.py --count 50 # siembra 50

La contraseña se toma de SUFI_LOAD_PASSWORD (defecto en loadtest_config). No se
imprime en claro. Los usuarios viven sólo en la DB de desarrollo (sufiatulado Docker).
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Permite importar `src.*` y `tests.load.*` al ejecutarse como script suelto.
_BACKEND_ROOT: Path = Path(__file__).resolve().parents[2]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

# El propio directorio (tests/load) está en sys.path[0] al ejecutarse como script.
import loadtest_config as cfg  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.infrastructure.config.settings import Settings  # noqa: E402
from src.infrastructure.security.password_hasher import PasswordHasher  # noqa: E402


def _crear_engine() -> AsyncEngine:
    settings: Settings = Settings()
    # Salvaguarda: nunca sembrar contra producción.
    if settings.app_env == "production":
        raise SystemExit("Negado: la siembra de carga no se ejecuta contra APP_ENV=production")
    return create_async_engine(settings.database_url, pool_pre_ping=True)


async def _sembrar(session: AsyncSession, count: int) -> int:
    hasher: PasswordHasher = PasswordHasher()
    # Una sola operación bcrypt: todos comparten la misma contraseña de prueba.
    nuevo_hash: str = hasher.hashear(cfg.LOADTEST_PASSWORD)
    creados: int = 0
    for i in range(1, count + 1):
        doc: str = cfg.documento_de_indice(i)
        # uid es IDENTITY en el snapshot → no se inserta explícito; se recupera por name.
        uid: int | None = (
            await session.execute(text("SELECT uid FROM users WHERE name = :name"), {"name": doc})
        ).scalar_one_or_none()
        if uid is None:
            # Las columnas NOT NULL no listadas usan su DEFAULT del esquema.
            await session.execute(
                text(
                    "INSERT INTO users (name, mail, new_pass, status, created, access) "
                    "VALUES (:name, :mail, :np, 1, 0, 0)"
                ),
                {"name": doc, "mail": f"{doc}@loadtest.sufi.local", "np": nuevo_hash},
            )
            uid = (
                await session.execute(text("SELECT uid FROM users WHERE name = :name"), {"name": doc})
            ).scalar_one()
            creados += 1
        else:
            await session.execute(
                text("UPDATE users SET new_pass = :np, status = 1 WHERE uid = :uid"),
                {"np": nuevo_hash, "uid": uid},
            )
        # Rol comisionista (idempotente).
        tiene_rol: int | None = (
            await session.execute(
                text("SELECT 1 FROM users_roles WHERE uid = :uid AND rid = :rid"),
                {"uid": uid, "rid": cfg.COMISIONISTA_RID},
            )
        ).scalar_one_or_none()
        if tiene_rol is None:
            await session.execute(
                text("INSERT INTO users_roles (uid, rid) VALUES (:uid, :rid)"),
                {"uid": uid, "rid": cfg.COMISIONISTA_RID},
            )
    await session.commit()
    return creados


async def _limpiar(session: AsyncSession) -> dict[str, int]:
    like: str = f"{cfg.LOADTEST_DOC_PREFIJO}%"
    borrados: dict[str, int] = {}
    # Perfiles (clave numero_documento).
    for tabla in ("users_perfil_contacto", "users_perfil_tributario", "users_perfil_emocional"):
        res = await session.execute(
            text(f"DELETE FROM {tabla} WHERE numero_documento LIKE :like"), {"like": like}
        )
        borrados[tabla] = res.rowcount or 0
    # Roles y usuarios: uid es IDENTITY → se identifican por name (== numero_documento).
    res_roles = await session.execute(
        text(
            "DELETE FROM users_roles WHERE uid IN "
            "(SELECT uid FROM users WHERE name LIKE :like)"
        ),
        {"like": like},
    )
    borrados["users_roles"] = res_roles.rowcount or 0
    res_users = await session.execute(
        text("DELETE FROM users WHERE name LIKE :like"), {"like": like}
    )
    borrados["users"] = res_users.rowcount or 0
    await session.commit()
    return borrados


async def _main_async(reset: bool, count: int) -> None:
    engine: AsyncEngine = _crear_engine()
    sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessionmaker() as session:
            if reset:
                borrados = await _limpiar(session)
                print(f"[reset] filas borradas: {borrados}")
            else:
                creados = await _sembrar(session, count)
                print(
                    f"[seed] {count} usuarios comisionista asegurados "
                    f"({creados} nuevos) — docs {cfg.documento_de_indice(1)}..{cfg.documento_de_indice(count)}"
                )
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Siembra/limpieza de usuarios de carga SUFI")
    parser.add_argument("--reset", action="store_true", help="Borra los usuarios y perfiles sembrados")
    parser.add_argument("--count", type=int, default=cfg.LOADTEST_COUNT, help="Cantidad de usuarios a sembrar")
    args = parser.parse_args()
    # En Windows el loop por defecto de asyncio sirve para aioodbc.
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(_main_async(args.reset, args.count))


if __name__ == "__main__":
    main()
