from __future__ import annotations

from typing import Final

from src.application.dto.pagina_usuarios_dto import PaginaUsuariosDTO
from src.domain.entities.rol_asignado_entity import RolAsignadoEntity
from src.domain.entities.rol_entity import RolEntity
from src.domain.entities.usuario_cuenta_entity import UsuarioCuentaEntity
from src.domain.ports.outbound.asignacion_roles_repository import AsignacionRolesRepository


class GestionarAsignacionRolesUseCase:
    """Asignación de usuarios a roles (AP-0054), lado de escritura del módulo de
    autorizaciones. Centraliza las reglas de seguridad para ser testeables sin HTTP:

    * Roles técnicos de Drupal (anónimo=1, autenticado=2) no son asignables: son
      implícitos y nunca se almacenan en dbo.users_roles.
    * Cuentas del sistema (anónimo=0, superusuario Drupal=1) son intocables.
    * Anti-lockout (AP-0053): un actor no puede quitarse a sí mismo el rol
      'administrator' (evita perder el acceso al panel administrativo).
    """

    _ROLES_TECNICOS: Final[frozenset[int]] = frozenset({1, 2})
    _UIDS_SISTEMA: Final[frozenset[int]] = frozenset({0, 1})
    _ROL_ADMINISTRATOR: Final[str] = "administrator"

    def __init__(self, asignacion_repo: AsignacionRolesRepository) -> None:
        self._repo: AsignacionRolesRepository = asignacion_repo

    async def listar_roles_async(self) -> list[RolEntity]:
        return await self._repo.listar_roles_asignables_async()

    async def listar_usuarios_de_rol_async(
        self, rid: int, texto: str | None, page: int, page_size: int
    ) -> PaginaUsuariosDTO:
        await self._validar_rol_asignable(rid)
        items: list[UsuarioCuentaEntity]
        total: int
        items, total = await self._repo.listar_usuarios_de_rol_async(rid, texto, page, page_size)
        return PaginaUsuariosDTO(items=items, total=total, page=page, page_size=page_size)

    async def buscar_usuarios_async(
        self, texto: str | None, page: int, page_size: int
    ) -> PaginaUsuariosDTO:
        items: list[UsuarioCuentaEntity]
        total: int
        items, total = await self._repo.buscar_usuarios_async(texto, page, page_size)
        return PaginaUsuariosDTO(items=items, total=total, page=page, page_size=page_size)

    async def obtener_roles_de_usuario_async(self, uid: int) -> list[RolAsignadoEntity]:
        self._validar_usuario_no_sistema(uid)
        await self._asegurar_usuario_existe(uid)
        return await self._repo.obtener_roles_de_usuario_async(uid)

    async def asignar_rol_async(self, actor_uid: int, uid: int, rid: int) -> bool:
        await self._validar_cambio(uid, rid)
        return await self._repo.asignar_rol_async(uid, rid)

    async def quitar_rol_async(self, actor_uid: int, uid: int, rid: int) -> bool:
        await self._validar_cambio(uid, rid)
        await self._validar_anti_lockout(actor_uid, uid, rid)
        return await self._repo.quitar_rol_async(uid, rid)

    def _validar_usuario_no_sistema(self, uid: int) -> None:
        if uid in self._UIDS_SISTEMA:
            raise ValueError("No se pueden gestionar los roles de esta cuenta del sistema")

    async def _validar_rol_asignable(self, rid: int) -> None:
        if rid in self._ROLES_TECNICOS:
            raise ValueError("Rol técnico no asignable (anónimo, autenticado)")
        if not await self._repo.existe_rol_async(rid):
            raise LookupError("Rol no encontrado")

    async def _asegurar_usuario_existe(self, uid: int) -> None:
        usuario: UsuarioCuentaEntity | None = await self._repo.obtener_usuario_async(uid)
        if usuario is None:
            raise LookupError("Usuario no encontrado")

    async def _validar_cambio(self, uid: int, rid: int) -> None:
        self._validar_usuario_no_sistema(uid)
        await self._validar_rol_asignable(rid)
        await self._asegurar_usuario_existe(uid)

    async def _validar_anti_lockout(self, actor_uid: int, uid: int, rid: int) -> None:
        if actor_uid != uid:
            return
        nombre: str | None = await self._repo.obtener_nombre_rol_async(rid)
        if nombre == self._ROL_ADMINISTRATOR:
            raise ValueError("No puedes quitarte a ti mismo el rol 'administrator'")
