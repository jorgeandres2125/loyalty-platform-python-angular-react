from __future__ import annotations

from typing import Final

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.shared.constants.minimo_privilegio import ANOMALIA_EXECUTE_BD

# HAS_PERMS_BY_NAME evalua el permiso del principal CONECTADO (la cuenta de la app), por lo
# que funciona con minimo privilegio sin leer catalogos del sistema. Devuelve 1 si la cuenta
# tiene EXECUTE a nivel de base de datos (alcanza a todo procedimiento o funcion, futuro
# incluido). La deteccion de GRANT al principal publico sobre objetos de usuario requiere
# lectura del catalogo y se realiza en el guard de CI y en el script de validacion del DBA.
_SQL_EXECUTE_BD: Final[str] = "SELECT HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'EXECUTE')"


class SqlServerSondaPermisosObjeto:
    """AP-0061: adaptador que autoevalua en SQL Server si la cuenta conectada por la app
    hereda permisos excesivos sobre objetos. Implementa SondaPermisosObjeto (PEP 544). Usa la
    fabrica de sesiones autonoma, independiente de la peticion.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession] | None) -> None:
        self._session_factory: async_sessionmaker[AsyncSession] | None = session_factory

    async def anomalias_minimo_privilegio(self) -> list[str]:
        if self._session_factory is None:
            raise RuntimeError(
                "Fabrica de sesiones no inicializada para el sondeo de permisos de objeto"
            )
        async with self._session_factory() as session:
            tiene_execute_bd: int | None = (
                await session.execute(text(_SQL_EXECUTE_BD))
            ).scalar()
        anomalias: list[str] = []
        if tiene_execute_bd == 1:
            anomalias.append(ANOMALIA_EXECUTE_BD)
        return anomalias
