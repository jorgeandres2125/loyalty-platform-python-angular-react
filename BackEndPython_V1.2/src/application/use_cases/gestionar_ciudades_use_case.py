from __future__ import annotations

from src.application.dto.ciudad_form_dto import CiudadFormDTO
from src.application.dto.ciudad_list_dto import CiudadListDTO
from src.application.dto.ciudad_list_item_dto import CiudadListItemDTO
from src.domain.entities.ciudad_entity import CiudadEntity
from src.domain.ports.outbound.ciudad_repository import CiudadRepository


class GestionarCiudadesUseCase:
    """CRUD admin sobre dbo.ciudades. Política 1C."""

    def __init__(self, ciudad_repo: CiudadRepository) -> None:
        self._ciudad_repo: CiudadRepository = ciudad_repo

    async def listar_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        did: int | None = None,
    ) -> CiudadListDTO:
        entities, total = await self._ciudad_repo.listar_paginado_async(
            page=page, page_size=page_size, nombre=nombre, did=did
        )
        items: list[CiudadListItemDTO] = [
            CiudadListItemDTO(cid=e.cid, did=e.did, ciudad=e.ciudad) for e in entities
        ]
        return CiudadListDTO(items=items, total=total, page=page, page_size=page_size)

    async def obtener_async(self, cid: int) -> CiudadEntity | None:
        return await self._ciudad_repo.obtener_por_id_async(cid)

    async def crear_async(self, dto: CiudadFormDTO) -> CiudadEntity:
        self._validar(dto)
        entity: CiudadEntity = CiudadEntity(
            cid=0, did=dto.did, ciudad=dto.ciudad.strip()
        )
        return await self._ciudad_repo.crear_async(entity)

    async def actualizar_async(
        self, cid: int, dto: CiudadFormDTO
    ) -> CiudadEntity | None:
        self._validar(dto)
        entity: CiudadEntity = CiudadEntity(
            cid=cid, did=dto.did, ciudad=dto.ciudad.strip()
        )
        return await self._ciudad_repo.actualizar_async(cid, entity)

    async def eliminar_async(self, cid: int) -> bool:
        if await self._ciudad_repo.existe_referenciado_async(cid):
            raise ValueError(
                "No se puede eliminar la ciudad porque está referenciada en perfiles de contacto"
            )
        return await self._ciudad_repo.eliminar_async(cid)

    @staticmethod
    def _validar(dto: CiudadFormDTO) -> None:
        if not dto.ciudad.strip():
            raise ValueError("El nombre de la ciudad es obligatorio")
        if len(dto.ciudad.strip()) > 50:
            raise ValueError("El nombre de la ciudad no puede exceder 50 caracteres")
