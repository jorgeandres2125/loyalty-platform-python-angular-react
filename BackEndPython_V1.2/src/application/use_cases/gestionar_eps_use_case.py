from __future__ import annotations

from src.application.dto.eps_form_dto import EpsFormDTO
from src.application.dto.eps_list_dto import EpsListDTO
from src.application.dto.eps_list_item_dto import EpsListItemDTO
from src.domain.entities.eps_entity import EpsEntity
from src.domain.ports.outbound.eps_repository import EpsRepository


class GestionarEpsUseCase:
    """CRUD admin sobre dbo.eps. Política 1C."""

    def __init__(self, eps_repo: EpsRepository) -> None:
        self._eps_repo: EpsRepository = eps_repo

    async def listar_async(
        self, page: int, page_size: int, nombre: str | None = None
    ) -> EpsListDTO:
        entities, total = await self._eps_repo.listar_paginado_async(
            page=page, page_size=page_size, nombre=nombre
        )
        items: list[EpsListItemDTO] = [
            EpsListItemDTO(tid=e.tid, nombre=e.nombre, nit=e.nit) for e in entities
        ]
        return EpsListDTO(items=items, total=total, page=page, page_size=page_size)

    async def obtener_async(self, tid: int) -> EpsEntity | None:
        return await self._eps_repo.obtener_por_id_async(tid)

    async def crear_async(self, dto: EpsFormDTO) -> EpsEntity:
        self._validar(dto)
        entity: EpsEntity = EpsEntity(
            tid=0,
            nombre=dto.nombre.strip(),
            nit=(dto.nit.strip() if dto.nit else None),
        )
        return await self._eps_repo.crear_async(entity)

    async def actualizar_async(self, tid: int, dto: EpsFormDTO) -> EpsEntity | None:
        self._validar(dto)
        entity: EpsEntity = EpsEntity(
            tid=tid,
            nombre=dto.nombre.strip(),
            nit=(dto.nit.strip() if dto.nit else None),
        )
        return await self._eps_repo.actualizar_async(tid, entity)

    async def eliminar_async(self, tid: int) -> bool:
        if await self._eps_repo.existe_referenciado_async(tid):
            raise ValueError(
                "No se puede eliminar la EPS porque está referenciada en perfiles tributarios"
            )
        return await self._eps_repo.eliminar_async(tid)

    @staticmethod
    def _validar(dto: EpsFormDTO) -> None:
        if not dto.nombre.strip():
            raise ValueError("El nombre de la EPS es obligatorio")
        if len(dto.nombre.strip()) > 200:
            raise ValueError("El nombre de la EPS no puede exceder 200 caracteres")
        if dto.nit is not None and len(dto.nit.strip()) > 30:
            raise ValueError("El NIT no puede exceder 30 caracteres")
