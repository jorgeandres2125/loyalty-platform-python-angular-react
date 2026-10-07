from __future__ import annotations

from src.application.dto.ejecutivo_form_dto import EjecutivoFormDTO
from src.application.dto.ejecutivo_list_dto import EjecutivoListDTO
from src.application.dto.ejecutivo_list_item_dto import EjecutivoListItemDTO
from src.domain.entities.ejecutivo_entity import EjecutivoEntity
from src.domain.ports.outbound.ejecutivo_repository import EjecutivoRepository
from src.shared.constants.perfiles_ejecutivo import (
    PERFILES_EJECUTIVO_NOMBRES,
    PERFILES_EJECUTIVO_VALIDOS,
    TIPOS_DOCUMENTO_EJECUTIVO,
)


class GestionarEjecutivosUseCase:
    def __init__(self, ejecutivo_repo: EjecutivoRepository) -> None:
        self._ejecutivo_repo: EjecutivoRepository = ejecutivo_repo

    @staticmethod
    def nombre_perfil(perfil: str) -> str:
        return PERFILES_EJECUTIVO_NOMBRES.get(perfil, perfil or "")

    async def listar_async(
        self,
        page: int,
        page_size: int,
        tipo_doc: str | None = None,
        documento: str | None = None,
        perfil: str | None = None,
        estado: bool | None = None,
    ) -> EjecutivoListDTO:
        entities, total = await self._ejecutivo_repo.listar_paginado_async(
            page=page,
            page_size=page_size,
            tipo_doc=tipo_doc,
            documento=documento,
            perfil=perfil,
            estado=estado,
        )
        items: list[EjecutivoListItemDTO] = [
            EjecutivoListItemDTO(
                id=entity.id or 0,
                tipo_documento=entity.tipo_documento,
                numero_documento=entity.numero_documento,
                nombre_completo=entity.nombre_completo,
                codigo_ejecutivo=entity.codigo_ejecutivo,
                celular=entity.celular,
                email=entity.email,
                perfil=entity.perfil,
                perfil_nombre=self.nombre_perfil(entity.perfil),
                estado=entity.estado,
            )
            for entity in entities
        ]
        return EjecutivoListDTO(items=items, total=total, page=page, page_size=page_size)

    async def obtener_async(self, ejecutivo_id: int) -> EjecutivoEntity | None:
        return await self._ejecutivo_repo.obtener_por_id_async(ejecutivo_id)

    async def crear_async(self, dto: EjecutivoFormDTO) -> EjecutivoEntity:
        self._validar(dto)
        repo = self._ejecutivo_repo
        duplicado: EjecutivoEntity | None = await repo.obtener_por_numero_documento_async(
            dto.numero_documento.strip()
        )
        if duplicado is not None:
            raise ValueError(
                f"Ya existe un ejecutivo con número de documento {dto.numero_documento}"
            )
        entity: EjecutivoEntity = self._to_entity(dto)
        return await self._ejecutivo_repo.crear_async(entity)

    async def actualizar_async(
        self, ejecutivo_id: int, dto: EjecutivoFormDTO
    ) -> EjecutivoEntity | None:
        self._validar(dto)
        repo = self._ejecutivo_repo
        otro: EjecutivoEntity | None = await repo.obtener_por_numero_documento_async(
            dto.numero_documento.strip()
        )
        if otro is not None and otro.id != ejecutivo_id:
            raise ValueError(
                f"Otro ejecutivo ya usa el número de documento {dto.numero_documento}"
            )
        entity: EjecutivoEntity = self._to_entity(dto)
        return await self._ejecutivo_repo.actualizar_async(ejecutivo_id, entity)

    @staticmethod
    def _validar(dto: EjecutivoFormDTO) -> None:
        if not dto.numero_documento.strip():
            raise ValueError("número de documento es obligatorio")
        if not dto.nombre_completo.strip():
            raise ValueError("nombre completo es obligatorio")
        if not dto.codigo_ejecutivo.strip():
            raise ValueError("código de ejecutivo es obligatorio")
        if not dto.email.strip():
            raise ValueError("email es obligatorio")
        if dto.tipo_documento and dto.tipo_documento not in TIPOS_DOCUMENTO_EJECUTIVO:
            raise ValueError(f"tipo de documento inválido: {dto.tipo_documento}")
        if dto.perfil not in PERFILES_EJECUTIVO_VALIDOS:
            raise ValueError(
                f"perfil inválido: {dto.perfil}. Valores válidos: "
                f"{sorted(PERFILES_EJECUTIVO_VALIDOS)}"
            )

    @staticmethod
    def _to_entity(dto: EjecutivoFormDTO) -> EjecutivoEntity:
        return EjecutivoEntity(
            tipo_documento=dto.tipo_documento.strip(),
            numero_documento=dto.numero_documento.strip(),
            nombre_completo=dto.nombre_completo.strip(),
            codigo_ejecutivo=dto.codigo_ejecutivo.strip(),
            celular=dto.celular.strip(),
            perfil=dto.perfil.strip(),
            email=dto.email.strip(),
            estado=dto.estado,
        )
