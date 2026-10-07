from __future__ import annotations

from src.application.dto.arl_form_dto import ArlFormDTO
from src.application.dto.arl_list_dto import ArlListDTO
from src.application.dto.arl_list_item_dto import ArlListItemDTO
from src.domain.entities.arl_entity import ArlEntity
from src.domain.ports.outbound.arl_repository import ArlRepository


class GestionarArlUseCase:
    """CRUD admin sobre dbo.arl. Política 1C: hard delete con guardia de FK."""

    def __init__(self, arl_repo: ArlRepository) -> None:
        self._arl_repo: ArlRepository = arl_repo

    async def listar_async(
        self, page: int, page_size: int, nombre: str | None = None
    ) -> ArlListDTO:
        entities, total = await self._arl_repo.listar_paginado_async(
            page=page, page_size=page_size, nombre=nombre
        )
        items: list[ArlListItemDTO] = [
            ArlListItemDTO(tid=e.tid, nombre=e.nombre, nit=e.nit) for e in entities
        ]
        return ArlListDTO(items=items, total=total, page=page, page_size=page_size)

    async def obtener_async(self, tid: int) -> ArlEntity | None:
        return await self._arl_repo.obtener_por_id_async(tid)

    async def crear_async(self, dto: ArlFormDTO) -> ArlEntity:
        self._validar(dto)
        entity: ArlEntity = ArlEntity(
            tid=0,
            nombre=dto.nombre.strip(),
            nit=(dto.nit.strip() if dto.nit else None),
        )
        return await self._arl_repo.crear_async(entity)

    async def actualizar_async(self, tid: int, dto: ArlFormDTO) -> ArlEntity | None:
        self._validar(dto)
        entity: ArlEntity = ArlEntity(
            tid=tid,
            nombre=dto.nombre.strip(),
            nit=(dto.nit.strip() if dto.nit else None),
        )
        return await self._arl_repo.actualizar_async(tid, entity)

    async def eliminar_async(self, tid: int) -> bool:
        if await self._arl_repo.existe_referenciado_async(tid):
            raise ValueError(
                "No se puede eliminar la ARL porque está referenciada en perfiles tributarios"
            )
        return await self._arl_repo.eliminar_async(tid)

    @staticmethod
    def _validar(dto: ArlFormDTO) -> None:
        if not dto.nombre.strip():
            raise ValueError("El nombre de la ARL es obligatorio")
        if len(dto.nombre.strip()) > 200:
            raise ValueError("El nombre de la ARL no puede exceder 200 caracteres")
        if dto.nit is not None and len(dto.nit.strip()) > 30:
            raise ValueError("El NIT no puede exceder 30 caracteres")
