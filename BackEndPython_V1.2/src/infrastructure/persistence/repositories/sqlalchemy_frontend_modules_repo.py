from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.modulo_permiso_entity import ModuloPermisoEntity

_SQL_MODULOS_POR_UID: str = """
SELECT
    fm.module_id,
    fm.module_code,
    fm.nombre,
    fm.ruta,
    fm.icono,
    fm.orden,
    MAX(CAST(fmp.puede_ver       AS int)) AS puede_ver,
    MAX(CAST(fmp.puede_crear     AS int)) AS puede_crear,
    MAX(CAST(fmp.puede_editar    AS int)) AS puede_editar,
    MAX(CAST(fmp.puede_eliminar  AS int)) AS puede_eliminar,
    MAX(CAST(fmp.puede_exportar  AS int)) AS puede_exportar,
    MAX(CAST(fmp.puede_aprobar   AS int)) AS puede_aprobar
FROM dbo.users u
INNER JOIN dbo.users_roles ur                       ON ur.uid       = u.uid
INNER JOIN dbo.role r                               ON r.rid        = ur.rid
INNER JOIN dbo.frontend_modules_permissions fmp     ON fmp.rid      = r.rid
INNER JOIN dbo.frontend_modules fm                  ON fm.module_id = fmp.module_id
WHERE u.uid = :uid
  AND u.status = 1
  AND fm.activo = 1
  AND fm.ruta IS NOT NULL
GROUP BY fm.module_id, fm.module_code, fm.nombre, fm.ruta, fm.icono, fm.orden
ORDER BY fm.orden, fm.module_id;
"""


class SQLAlchemyFrontendModulesRepo:
    """Resuelve los módulos del frontend con permisos efectivos para un usuario.

    Semántica de unión: si CUALQUIER rol del usuario otorga el flag, queda otorgado
    (MAX por flag en el GROUP BY). El rol más permisivo gana.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def obtener_modulos_por_uid_async(self, uid: int) -> list[ModuloPermisoEntity]:
        result = await self._session.execute(text(_SQL_MODULOS_POR_UID), {"uid": uid})
        rows = result.mappings().all()
        return [
            ModuloPermisoEntity(
                module_id=row["module_id"],
                module_code=row["module_code"],
                nombre=row["nombre"],
                ruta=row["ruta"],
                icono=row["icono"],
                orden=row["orden"],
                puede_ver=bool(row["puede_ver"]),
                puede_crear=bool(row["puede_crear"]),
                puede_editar=bool(row["puede_editar"]),
                puede_eliminar=bool(row["puede_eliminar"]),
                puede_exportar=bool(row["puede_exportar"]),
                puede_aprobar=bool(row["puede_aprobar"]),
            )
            for row in rows
        ]
