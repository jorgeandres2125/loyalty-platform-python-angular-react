from __future__ import annotations

from src.domain.entities.autorizacion_modulo_entity import AutorizacionModuloEntity
from src.domain.entities.rol_entity import RolEntity
from src.domain.ports.outbound.autorizaciones_repository import AutorizacionesRepository
from src.domain.value_objects.permisos_modulo import PermisosModulo


class GestionarAutorizacionesUseCase:
    """Parametrización de autorizaciones rol × módulo (AP-0054).

    Es el módulo de configuración de las autorizaciones de los usuarios: lista
    los roles, expone la matriz de permisos de cada rol y persiste los cambios.
    """

    def __init__(self, autorizaciones_repo: AutorizacionesRepository) -> None:
        self._repo: AutorizacionesRepository = autorizaciones_repo

    async def listar_roles_async(self) -> list[RolEntity]:
        return await self._repo.listar_roles_async()

    async def obtener_matriz_async(self, rid: int) -> list[AutorizacionModuloEntity]:
        return await self._repo.obtener_matriz_por_rol_async(rid)

    async def actualizar_permisos_async(
        self, rid: int, module_id: int, flags: PermisosModulo
    ) -> AutorizacionModuloEntity | None:
        self._validar_coherencia(flags)
        return await self._repo.actualizar_permisos_async(rid, module_id, flags)

    @staticmethod
    def _validar_coherencia(flags: PermisosModulo) -> None:
        """`puede_ver` es la base de todo acceso al módulo: sin ver no se puede
        crear, editar, eliminar, exportar ni aprobar. Evita estados incoherentes
        en los que un rol tiene acciones sobre un módulo que no puede abrir."""
        if flags.tiene_alguna_accion and not flags.puede_ver:
            raise ValueError(
                "Incoherencia de permisos: no se puede otorgar una acción "
                "(crear/editar/eliminar/exportar/aprobar) sin 'puede_ver'"
            )

    async def actualizar_activo_modulo_async(self, module_id: int, activo: bool) -> object:
        return await self._repo.actualizar_activo_modulo_async(module_id, activo)
