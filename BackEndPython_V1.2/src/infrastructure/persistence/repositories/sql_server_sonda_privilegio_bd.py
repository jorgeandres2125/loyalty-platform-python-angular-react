from __future__ import annotations

from typing import Final

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.shared.constants.minimo_privilegio import (
    ROL_SERVIDOR_SYSADMIN,
    ROLES_BD_PRIVILEGIADOS,
)

# Orden de las columnas devueltas por _SQL_ROLES (paralelo, 1 = pertenece al rol). El rol
# de servidor (IS_SRVROLEMEMBER) va primero; el resto son de BD (IS_ROLEMEMBER). Nombres
# de rol fijos definidos en shared/constants (no entrada del usuario): sin riesgo de
# inyeccion al interpolarlos en el SQL.
_COLUMNAS_ROLES: Final[tuple[str, ...]] = (ROL_SERVIDOR_SYSADMIN, *ROLES_BD_PRIVILEGIADOS)
_SQL_ROLES: Final[str] = "SELECT " + ", ".join(
    [f"IS_SRVROLEMEMBER('{ROL_SERVIDOR_SYSADMIN}')"]
    + [f"IS_ROLEMEMBER('{rol}')" for rol in ROLES_BD_PRIVILEGIADOS]
)


class SqlServerSondaPrivilegioBd:
    """AP-0056: adaptador que consulta a SQL Server que roles privilegiados tiene el
    principal conectado. Implementa SondaPrivilegioBd (PEP 544). Usa la fabrica de sesiones
    autonoma (misma via que la auditoria), independiente de la peticion.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession] | None) -> None:
        self._session_factory: async_sessionmaker[AsyncSession] | None = session_factory

    async def roles_privilegiados(self) -> list[str]:
        if self._session_factory is None:
            raise RuntimeError(
                "Fabrica de sesiones no inicializada para el sondeo de privilegio de BD"
            )
        async with self._session_factory() as session:
            fila = (await session.execute(text(_SQL_ROLES))).one()
        return [
            rol
            for rol, valor in zip(_COLUMNAS_ROLES, fila, strict=True)
            if valor == 1
        ]
