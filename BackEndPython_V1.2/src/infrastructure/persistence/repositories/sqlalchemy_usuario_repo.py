from __future__ import annotations

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.value_objects.estado_usuario import EstadoUsuario
from src.domain.value_objects.rol_usuario import RolUsuario
from src.infrastructure.persistence.models.drupal_user_model import DrupalUserModel


class SQLAlchemyUsuarioRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def obtener_por_nombre_async(self, nombre: str) -> UsuarioEntity | None:
        result = await self._session.execute(
            select(DrupalUserModel).where(
                DrupalUserModel.name == nombre,
                DrupalUserModel.status == 1,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def obtener_por_uid_async(self, uid: int) -> UsuarioEntity | None:
        result = await self._session.execute(
            select(DrupalUserModel).where(
                DrupalUserModel.uid == uid,
                DrupalUserModel.status == 1,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def actualizar_password_async(self, uid: int, nuevo_hash: str) -> None:
        await self._session.execute(
            update(DrupalUserModel)
            .where(DrupalUserModel.uid == uid)
            .values(new_pass=nuevo_hash)
        )
        await self._session.flush()

    # --- AP-0001: gestión de estado de cuenta ---

    async def listar_paginado_async(
        self, page: int, page_size: int, texto: str | None, activo: bool | None
    ) -> tuple[list[UsuarioEntity], int]:
        # uid > 1 excluye al anónimo (0) y al superusuario Drupal (1)
        base = select(DrupalUserModel).where(DrupalUserModel.uid > 1)
        if texto:
            patron: str = f"%{texto.strip()}%"
            base = base.where(
                or_(DrupalUserModel.name.like(patron), DrupalUserModel.mail.like(patron))
            )
        if activo is not None:
            base = base.where(DrupalUserModel.status == (1 if activo else 0))
        total: int = (
            await self._session.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()
        stmt = (
            base.order_by(DrupalUserModel.name)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows], total

    async def obtener_cualquiera_por_uid_async(self, uid: int) -> UsuarioEntity | None:
        result = await self._session.execute(
            select(DrupalUserModel).where(DrupalUserModel.uid == uid)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def actualizar_estado_async(self, uid: int, activo: bool) -> None:
        await self._session.execute(
            update(DrupalUserModel)
            .where(DrupalUserModel.uid == uid)
            .values(status=1 if activo else 0)
        )
        await self._session.flush()

    async def obtener_uid_por_documento_async(self, numero_documento: str) -> int | None:
        result = await self._session.execute(
            select(DrupalUserModel.uid)
            .where(DrupalUserModel.name == numero_documento)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def resolver_estado(self, uid: int) -> EstadoUsuario:
        # AP-0133 y AP-0049: verificacion viva del estado por PK (una consulta, sin cargar
        # roles). Fila ausente -> ELIMINADO; status != 1 (deshabilitada o dada de baja
        # logica) -> INHABILITADO; en otro caso ACTIVO. El bloqueo temporal por intentos
        # (AP-0009) se resuelve aparte en el ServicioBloqueoCuenta, no aqui.
        result = await self._session.execute(
            select(DrupalUserModel.status).where(DrupalUserModel.uid == uid)
        )
        status_val: int | None = result.scalar_one_or_none()
        if status_val is None:
            return EstadoUsuario.ELIMINADO
        if status_val != 1:
            return EstadoUsuario.INHABILITADO
        return EstadoUsuario.ACTIVO

    @staticmethod
    def _to_entity(model: DrupalUserModel) -> UsuarioEntity:
        roles: list[RolUsuario] = []
        for ur in (model.roles or []):
            if ur.rol:
                try:
                    roles.append(RolUsuario.desde_legacy(ur.rol.name))
                except ValueError:
                    pass
        return UsuarioEntity(
            uid=model.uid,
            nombre=model.name or "",
            email=model.mail or "",
            roles=roles,
            activo=(model.status == 1),
            password_hash=model.pass_,
            new_pass_hash=model.new_pass,
        )
