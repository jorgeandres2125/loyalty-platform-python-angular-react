from __future__ import annotations

from src.application.dto.profesion_form_dto import ProfesionFormDTO
from src.application.dto.profesion_list_dto import ProfesionListDTO
from src.application.dto.profesion_list_item_dto import ProfesionListItemDTO
from src.domain.entities.profesion_entity import ProfesionEntity
from src.domain.ports.outbound.profesion_repository import ProfesionRepository


class GestionarProfesionesUseCase:
    """CRUD admin sobre dbo.taxonomia_profesion. Política 1C.

    El guardia de delete compara por NOMBRE (no por tid) porque la columna
    users_perfil_emocional.profesion es String(220).
    """

    def __init__(self, profesion_repo: ProfesionRepository) -> None:
        self._profesion_repo: ProfesionRepository = profesion_repo

    async def listar_async(
        self, page: int, page_size: int, nombre: str | None = None
    ) -> ProfesionListDTO:
        entities, total = await self._profesion_repo.listar_paginado_async(
            page=page, page_size=page_size, nombre=nombre
        )
        items: list[ProfesionListItemDTO] = [
            ProfesionListItemDTO(tid=e.tid, nombre=e.nombre) for e in entities
        ]
        return ProfesionListDTO(items=items, total=total, page=page, page_size=page_size)

    async def obtener_async(self, tid: int) -> ProfesionEntity | None:
        return await self._profesion_repo.obtener_por_id_async(tid)

    async def crear_async(self, dto: ProfesionFormDTO) -> ProfesionEntity:
        self._validar(dto)
        entity: ProfesionEntity = ProfesionEntity(tid=0, nombre=dto.nombre.strip())
        return await self._profesion_repo.crear_async(entity)

    async def actualizar_async(
        self, tid: int, dto: ProfesionFormDTO
    ) -> ProfesionEntity | None:
        self._validar(dto)
        entity: ProfesionEntity = ProfesionEntity(tid=tid, nombre=dto.nombre.strip())
        return await self._profesion_repo.actualizar_async(tid, entity)

    async def eliminar_async(self, tid: int) -> bool:
        actual: ProfesionEntity | None = await self._profesion_repo.obtener_por_id_async(tid)
        if actual is None:
            return False
        if await self._profesion_repo.existe_referenciado_async(tid, actual.nombre):
            raise ValueError(
                "No se puede eliminar la profesión porque está referenciada en perfiles emocionales"
            )
        return await self._profesion_repo.eliminar_async(tid)

    @staticmethod
    def _validar(dto: ProfesionFormDTO) -> None:
        if not dto.nombre.strip():
            raise ValueError("El nombre de la profesión es obligatorio")
        if len(dto.nombre.strip()) > 220:
            raise ValueError("El nombre de la profesión no puede exceder 220 caracteres")
