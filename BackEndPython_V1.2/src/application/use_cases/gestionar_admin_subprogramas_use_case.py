from __future__ import annotations

from src.application.dto.admin_subprograma_form_dto import AdminSubprogramaFormDTO
from src.application.dto.admin_subprograma_list_dto import AdminSubprogramaListDTO
from src.application.dto.admin_subprograma_list_item_dto import (
    AdminSubprogramaListItemDTO,
)
from src.domain.entities.comisionista_subprograma_entity import (
    ComisionistaSubprogramaEntity,
)
from src.domain.ports.outbound.admin_subprograma_repository import (
    AdminSubprogramaRepository,
)


class GestionarAdminSubprogramasUseCase:
    """CRUD admin sobre dbo.comisionistas_subprograma. Política 1C."""

    def __init__(self, subprograma_repo: AdminSubprogramaRepository) -> None:
        self._subprograma_repo: AdminSubprogramaRepository = subprograma_repo

    async def listar_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        cpid: int | None = None,
    ) -> AdminSubprogramaListDTO:
        entities, total = await self._subprograma_repo.listar_paginado_async(
            page=page, page_size=page_size, nombre=nombre, cpid=cpid
        )
        items: list[AdminSubprogramaListItemDTO] = [
            AdminSubprogramaListItemDTO(
                cspid=e.cspid or 0, cspid_nombre=e.cspid_nombre, cpid=e.cpid
            )
            for e in entities
        ]
        return AdminSubprogramaListDTO(
            items=items, total=total, page=page, page_size=page_size
        )

    async def obtener_async(
        self, cspid: int
    ) -> ComisionistaSubprogramaEntity | None:
        return await self._subprograma_repo.obtener_por_id_async(cspid)

    async def crear_async(
        self, dto: AdminSubprogramaFormDTO
    ) -> ComisionistaSubprogramaEntity:
        self._validar(dto)
        entity: ComisionistaSubprogramaEntity = ComisionistaSubprogramaEntity(
            cspid=None, cspid_nombre=dto.cspid_nombre.strip(), cpid=dto.cpid
        )
        return await self._subprograma_repo.crear_async(entity)

    async def actualizar_async(
        self, cspid: int, dto: AdminSubprogramaFormDTO
    ) -> ComisionistaSubprogramaEntity | None:
        self._validar(dto)
        entity: ComisionistaSubprogramaEntity = ComisionistaSubprogramaEntity(
            cspid=cspid, cspid_nombre=dto.cspid_nombre.strip(), cpid=dto.cpid
        )
        return await self._subprograma_repo.actualizar_async(cspid, entity)

    async def eliminar_async(self, cspid: int) -> bool:
        if await self._subprograma_repo.existe_referenciado_async(cspid):
            raise ValueError(
                "No se puede eliminar el sub-programa porque está referenciado por canales"
            )
        return await self._subprograma_repo.eliminar_async(cspid)

    @staticmethod
    def _validar(dto: AdminSubprogramaFormDTO) -> None:
        if not dto.cspid_nombre.strip():
            raise ValueError("El nombre del sub-programa es obligatorio")
        if len(dto.cspid_nombre.strip()) > 45:
            raise ValueError("El nombre del sub-programa no puede exceder 45 caracteres")
