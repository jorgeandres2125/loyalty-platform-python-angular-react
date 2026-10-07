from __future__ import annotations

from src.application.dto.departamento_form_dto import DepartamentoFormDTO
from src.application.dto.departamento_list_dto import DepartamentoListDTO
from src.application.dto.departamento_list_item_dto import DepartamentoListItemDTO
from src.domain.entities.departamento_entity import DepartamentoEntity
from src.domain.ports.outbound.departamento_repository import DepartamentoRepository


class GestionarDepartamentosUseCase:
    """CRUD admin sobre dbo.departamentos. Política 1C con dos guardias de FK."""

    def __init__(self, departamento_repo: DepartamentoRepository) -> None:
        self._departamento_repo: DepartamentoRepository = departamento_repo

    async def listar_async(
        self, page: int, page_size: int, nombre: str | None = None
    ) -> DepartamentoListDTO:
        entities, total = await self._departamento_repo.listar_paginado_async(
            page=page, page_size=page_size, nombre=nombre
        )
        items: list[DepartamentoListItemDTO] = [
            DepartamentoListItemDTO(did=e.did, pid=e.pid, departamento=e.departamento)
            for e in entities
        ]
        return DepartamentoListDTO(items=items, total=total, page=page, page_size=page_size)

    async def obtener_async(self, did: int) -> DepartamentoEntity | None:
        return await self._departamento_repo.obtener_por_id_async(did)

    async def crear_async(self, dto: DepartamentoFormDTO) -> DepartamentoEntity:
        self._validar(dto)
        entity: DepartamentoEntity = DepartamentoEntity(
            did=0, pid=dto.pid, departamento=dto.departamento.strip()
        )
        return await self._departamento_repo.crear_async(entity)

    async def actualizar_async(
        self, did: int, dto: DepartamentoFormDTO
    ) -> DepartamentoEntity | None:
        self._validar(dto)
        entity: DepartamentoEntity = DepartamentoEntity(
            did=did, pid=dto.pid, departamento=dto.departamento.strip()
        )
        return await self._departamento_repo.actualizar_async(did, entity)

    async def eliminar_async(self, did: int) -> bool:
        if await self._departamento_repo.existe_referenciado_async(did):
            raise ValueError(
                "No se puede eliminar el departamento porque tiene ciudades hijas o está referenciado en perfiles de contacto"
            )
        return await self._departamento_repo.eliminar_async(did)

    @staticmethod
    def _validar(dto: DepartamentoFormDTO) -> None:
        if not dto.departamento.strip():
            raise ValueError("El nombre del departamento es obligatorio")
        if len(dto.departamento.strip()) > 50:
            raise ValueError("El nombre del departamento no puede exceder 50 caracteres")
