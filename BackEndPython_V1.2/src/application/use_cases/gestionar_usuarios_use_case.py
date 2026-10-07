from __future__ import annotations

from typing import Final

from src.application.dto.usuario_list_dto import UsuarioListDTO
from src.application.dto.usuario_list_item_dto import UsuarioListItemDTO
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.permiso_denegado import PermisoDenegado
from src.domain.ports.outbound.estado_credencial_repository import EstadoCredencialRepository
from src.domain.ports.outbound.usuario_repository import UsuarioRepository
from src.domain.value_objects.rol_usuario import RolUsuario


class GestionarUsuariosUseCase:
    """Caso de uso administrativo (AP-0001): habilitar / deshabilitar cuentas de usuario.

    Deshabilitar fija dbo.users.status = 0, lo que expulsa al usuario en el
    siguiente login (la consulta de autenticación filtra status == 1).

    Reglas de negocio (matriz quién-puede-sobre-quién), centralizadas aquí para
    ser testeables sin HTTP:

    * No se puede tocar el anónimo (uid 0) ni el superusuario Drupal (uid 1).
    * Nadie puede deshabilitar su propia cuenta (anti auto-bloqueo).
    * Actor administrator/webmaster: cualquier cuenta, salvo deshabilitar a otro
      administrator (anti-sabotaje/escalada).
    * Actor no administrativo (asesor/ejecutivo): sólo puede actuar sobre cuentas
      cuyos roles sean exclusivamente de comisionista.
    """

    _UID_ANONIMO: Final[int] = 0
    _UID_SUPERUSUARIO: Final[int] = 1
    _ROLES_ADMINISTRATIVOS: Final[frozenset[RolUsuario]] = frozenset(
        {RolUsuario.ADMINISTRATOR, RolUsuario.WEBMASTER}
    )
    _ROLES_COMISIONISTA: Final[frozenset[RolUsuario]] = frozenset(
        {RolUsuario.COMISIONISTA, RolUsuario.COMISIONISTA_CONSUMO}
    )

    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        estado_credencial: EstadoCredencialRepository | None = None,
    ) -> None:
        self._usuario_repo: UsuarioRepository = usuario_repo
        self._estado_credencial: EstadoCredencialRepository | None = estado_credencial

    async def listar_async(
        self,
        page: int,
        page_size: int,
        texto: str | None = None,
        activo: bool | None = None,
    ) -> UsuarioListDTO:
        entidades, total = await self._usuario_repo.listar_paginado_async(
            page=page,
            page_size=page_size,
            texto=texto,
            activo=activo,
        )
        items: list[UsuarioListItemDTO] = [
            UsuarioListItemDTO(
                uid=entidad.uid if entidad.uid is not None else 0,
                nombre=entidad.nombre,
                email=entidad.email,
                activo=entidad.activo,
                roles=[rol.value for rol in entidad.roles],
            )
            for entidad in entidades
        ]
        return UsuarioListDTO(items=items, total=total, page=page, page_size=page_size)

    async def cambiar_estado_async(
        self,
        uid_objetivo: int,
        activo: bool,
        actor_uid: int,
        actor_roles: list[RolUsuario],
    ) -> UsuarioEntity:
        if uid_objetivo in (self._UID_ANONIMO, self._UID_SUPERUSUARIO):
            raise ValueError("No se puede modificar el estado de esta cuenta del sistema")
        if uid_objetivo == actor_uid and not activo:
            raise ValueError("No puedes deshabilitar tu propia cuenta")

        objetivo: UsuarioEntity | None = await self._usuario_repo.obtener_cualquiera_por_uid_async(
            uid_objetivo
        )
        if objetivo is None:
            raise LookupError("Usuario no encontrado")

        es_actor_admin: bool = bool(self._ROLES_ADMINISTRATIVOS & set(actor_roles))
        if es_actor_admin:
            if objetivo.tiene_rol(RolUsuario.ADMINISTRATOR) and not activo:
                raise ValueError(
                    "No se puede deshabilitar a otro administrador desde este panel"
                )
        else:
            if not objetivo.roles or not set(objetivo.roles) <= self._ROLES_COMISIONISTA:
                raise PermisoDenegado("USUARIOS_GESTIONAR_ESTADO")

        await self._usuario_repo.actualizar_estado_async(uid_objetivo, activo)
        if not activo and self._estado_credencial is not None:
            # AP-0021: deshabilitar invalida las sesiones vivas del usuario (token_version++).
            await self._estado_credencial.incrementar_version(uid_objetivo)
        objetivo.activo = activo
        return objetivo

    async def eliminar_async(
        self,
        uid_objetivo: int,
        actor_uid: int,
        actor_roles: list[RolUsuario],
    ) -> UsuarioEntity:
        """AP-0049: eliminacion logica de la cuenta (status = 0) con revocacion
        inmediata de las sesiones vivas (token_version++). Solo actores
        administrativos; sin borrado fisico de dbo.users (retencion AP-0026 e
        integridad referencial legacy)."""
        if uid_objetivo in (self._UID_ANONIMO, self._UID_SUPERUSUARIO):
            raise ValueError("No se puede eliminar esta cuenta del sistema")
        if uid_objetivo == actor_uid:
            raise ValueError("No puedes eliminar tu propia cuenta")
        if not self._ROLES_ADMINISTRATIVOS & set(actor_roles):
            raise PermisoDenegado("USUARIOS_ELIMINAR")

        objetivo: UsuarioEntity | None = (
            await self._usuario_repo.obtener_cualquiera_por_uid_async(uid_objetivo)
        )
        if objetivo is None:
            raise LookupError("Usuario no encontrado")
        if objetivo.tiene_rol(RolUsuario.ADMINISTRATOR):
            raise ValueError(
                "No se puede eliminar a otro administrador desde este panel"
            )

        await self._usuario_repo.actualizar_estado_async(uid_objetivo, False)
        if self._estado_credencial is not None:
            # AP-0049: invalida en el acto todas las sesiones vivas del usuario.
            await self._estado_credencial.incrementar_version(uid_objetivo)
        objetivo.activo = False
        return objetivo

    async def cambiar_estado_por_documento_async(
        self,
        numero_documento: str,
        activo: bool,
        actor_uid: int,
        actor_roles: list[RolUsuario],
    ) -> UsuarioEntity:
        uid: int | None = await self._usuario_repo.obtener_uid_por_documento_async(
            numero_documento
        )
        if uid is None:
            raise LookupError("El comisionista no tiene una cuenta de acceso asociada")
        return await self.cambiar_estado_async(
            uid_objetivo=uid,
            activo=activo,
            actor_uid=actor_uid,
            actor_roles=actor_roles,
        )
