from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.documento_entity import DocumentoEntity
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.entities.perfil_emocional_entity import PerfilEmocionalEntity
from src.domain.entities.perfil_tributario_entity import PerfilTributarioEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.perfil_no_encontrado import PerfilNoEncontrado
from src.domain.ports.outbound.documento_repository import DocumentoRepository
from src.domain.ports.outbound.perfil_repository import PerfilRepository
from src.domain.ports.outbound.usuario_repository import UsuarioRepository
from src.infrastructure.persistence.models.ciudad_model import CiudadModel
from src.infrastructure.persistence.models.departamento_model import DepartamentoModel

# Los roles del JWT vienen como `RolUsuario.value` (slug con underscore),
# no con el nombre legacy con espacios.
_ROL_MOVILIDAD = "comisionista"
_ROL_CONSUMO = "comisionista_consumo"
_TIPOS_DOC = {4: "cedula", 5: "rut", 6: "contrato"}


class MiPerfilUseCase:
    """Caso de uso: el comisionista logueado lee y edita sus propios datos.

    Resuelve `numero_documento` desde el JWT (sub=uid → dbo.users.name) y delega a
    los repositorios existentes. No expone datos de otros usuarios.
    """

    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        perfil_repo: PerfilRepository,
        documento_repo: DocumentoRepository,
    ) -> None:
        self._usuario_repo: UsuarioRepository = usuario_repo
        self._perfil_repo: PerfilRepository = perfil_repo
        self._documento_repo: DocumentoRepository = documento_repo

    async def resolver_numero_documento_async(self, uid: int) -> str:
        usuario: UsuarioEntity | None = await self._usuario_repo.obtener_por_uid_async(uid)
        if usuario is None:
            raise PerfilNoEncontrado(f"No se encontró usuario con uid={uid}")
        return usuario.nombre

    # ── Contacto ──────────────────────────────────────────────────────────────
    async def obtener_contacto_async(self, uid: int) -> PerfilContactoEntity | None:
        numero_documento: str = await self.resolver_numero_documento_async(uid)
        return await self._perfil_repo.obtener_contacto_async(numero_documento)

    async def guardar_contacto_async(
        self, uid: int, entity: PerfilContactoEntity
    ) -> PerfilContactoEntity:
        numero_documento: str = await self.resolver_numero_documento_async(uid)
        entity.numero_documento = numero_documento
        return await self._perfil_repo.guardar_contacto_async(entity)

    # ── Tributario (sólo Movilidad) ──────────────────────────────────────────
    async def obtener_tributario_async(self, uid: int) -> PerfilTributarioEntity | None:
        numero_documento: str = await self.resolver_numero_documento_async(uid)
        return await self._perfil_repo.obtener_tributario_async(numero_documento)

    async def guardar_tributario_async(
        self, uid: int, entity: PerfilTributarioEntity
    ) -> PerfilTributarioEntity:
        numero_documento: str = await self.resolver_numero_documento_async(uid)
        entity.numero_documento = numero_documento
        return await self._perfil_repo.guardar_tributario_async(entity)

    # ── Emocional ────────────────────────────────────────────────────────────
    async def obtener_emocional_async(self, uid: int) -> PerfilEmocionalEntity | None:
        numero_documento: str = await self.resolver_numero_documento_async(uid)
        return await self._perfil_repo.obtener_emocional_async(numero_documento)

    async def guardar_emocional_async(
        self, uid: int, entity: PerfilEmocionalEntity
    ) -> PerfilEmocionalEntity:
        numero_documento: str = await self.resolver_numero_documento_async(uid)
        entity.numero_documento = numero_documento
        return await self._perfil_repo.guardar_emocional_async(entity)

    # ── Dashboard (agregado: estado del perfil + documentos + datos clave) ──
    async def obtener_dashboard_async(
        self, uid: int, roles: list[str], session: AsyncSession | None = None
    ) -> dict[str, Any]:
        numero_documento: str = await self.resolver_numero_documento_async(uid)
        es_movilidad: bool = _ROL_MOVILIDAD in roles
        es_consumo: bool = _ROL_CONSUMO in roles

        contacto: PerfilContactoEntity | None = await self._perfil_repo.obtener_contacto_async(numero_documento)
        emocional: PerfilEmocionalEntity | None = await self._perfil_repo.obtener_emocional_async(numero_documento)
        tributario: PerfilTributarioEntity | None = (
            await self._perfil_repo.obtener_tributario_async(numero_documento)
            if es_movilidad else None
        )

        contacto_completo: bool = bool(
            contacto and contacto.nombre_completo and contacto.celular and contacto.direccion
        )
        emocional_completo: bool = bool(emocional and emocional.estado_civil)
        tributario_completo: bool | None = (
            bool(tributario and (tributario.total or 0) > 0)
            if es_movilidad else None
        )

        stages_total: int = 2 + (1 if es_movilidad else 0)
        stages_completos: int = (
            (1 if contacto_completo else 0)
            + (1 if emocional_completo else 0)
            + ((1 if tributario_completo else 0) if es_movilidad else 0)
        )
        porcentaje: int = int(stages_completos * 100 / stages_total) if stages_total else 0

        # Documentos sólo aplican a Movilidad
        documentos_info: dict[str, Any] | None = None
        if es_movilidad:
            docs: list[DocumentoEntity] = await self._documento_repo.listar_por_asesor_async(numero_documento)
            por_tipo: dict[int, DocumentoEntity] = {doc.tipo: doc for doc in docs}
            documentos_info = {
                "items": {
                    nombre: (
                        {"subido": True, "estado": por_tipo[tipo].estado, "version": por_tipo[tipo].version}
                        if tipo in por_tipo else {"subido": False, "estado": None, "version": 0}
                    )
                    for tipo, nombre in _TIPOS_DOC.items()
                },
                "total_subidos": len(por_tipo),
                "total_esperados": len(_TIPOS_DOC),
                "total_aprobados": sum(1 for doc in docs if (doc.estado or "").lower() == "aprobado"),
            }

        programa: dict[str, Any] | None = None
        if contacto and contacto.comisionista_programa_id:
            programa = {
                "cpid": contacto.comisionista_programa_id,
                "nombre": "Movilidad" if contacto.comisionista_programa_id == 1 else "Consumo y Servicios",
            }

        # Resolver nombres de departamento/ciudad para que el dashboard los muestre
        # sin requerir 2 peticiones adicionales del frontend.
        departamento_nombre: str | None = None
        ciudad_nombre: str | None = None
        if session is not None and contacto:
            try:
                if contacto.departamento:
                    did: int = int(contacto.departamento)
                    dep_row = await session.execute(
                        select(DepartamentoModel.departamento).where(DepartamentoModel.did == did)
                    )
                    departamento_nombre = dep_row.scalar_one_or_none()
                if contacto.ciudad:
                    cid: int = int(contacto.ciudad)
                    ciu_row = await session.execute(
                        select(CiudadModel.ciudad).where(CiudadModel.cid == cid)
                    )
                    ciudad_nombre = ciu_row.scalar_one_or_none()
            except (TypeError, ValueError):
                pass

        return {
            "numero_documento": numero_documento,
            "nombre_completo": (contacto.nombre_completo if contacto else "") or "",
            "celular": contacto.celular if contacto else None,
            "email": contacto.email if contacto else None,
            "direccion": contacto.direccion if contacto else None,
            "departamento": contacto.departamento if contacto else None,
            "ciudad": contacto.ciudad if contacto else None,
            "departamento_nombre": departamento_nombre,
            "ciudad_nombre": ciudad_nombre,
            "programa": programa,
            "incentivos_habilitados": bool(contacto and contacto.incentivos),
            "rol_principal": _ROL_MOVILIDAD if es_movilidad else (_ROL_CONSUMO if es_consumo else "otro"),
            "perfil": {
                "contacto_completo": contacto_completo,
                "tributario_completo": tributario_completo,
                "emocional_completo": emocional_completo,
                "stages_completos": stages_completos,
                "stages_total": stages_total,
                "porcentaje_completado": porcentaje,
            },
            "documentos": documentos_info,
        }
