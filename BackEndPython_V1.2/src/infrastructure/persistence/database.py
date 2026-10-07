from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.persistence.base import Base  # noqa: F401

_engine = None
_session_factory = None


def init_db(
    database_url: str,
    *,
    pool_size: int = 10,
    max_overflow: int = 90,
    pool_timeout: int = 30,
    pool_recycle: int = 3600,
    echo: bool = False,
) -> None:
    global _engine, _session_factory
    _engine = create_async_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
    )
    _session_factory = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )


async def get_db_session_async() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        raise RuntimeError(
            "Base de datos no inicializada — llama a init_db() en el lifespan"
        )
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_session_factory() -> async_sessionmaker[AsyncSession] | None:
    """AP-0028: expone la fabrica de sesiones para escrituras autonomas (auditoria)."""
    return _session_factory


async def dispose_engine() -> None:
    if _engine is not None:
        await _engine.dispose()

async def reiniciar_engine_por_rotacion(
    database_url: str,
    *,
    pool_size: int = 10,
    max_overflow: int = 90,
    pool_timeout: int = 30,
    pool_recycle: int = 3600,
    echo: bool = False,
) -> None:
    """AP-0062: ante rotacion de la credencial de BD por la herramienta PAM, descarta el pool
    actual (cuyas conexiones usan la credencial anterior) y reconstruye el engine con la nueva
    URL resuelta desde el proveedor de secretos. Permite rotar sin redeploy."""
    await dispose_engine()
    init_db(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        echo=echo,
    )
