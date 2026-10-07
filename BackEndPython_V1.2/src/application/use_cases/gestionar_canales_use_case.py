from __future__ import annotations

from src.application.dto.canal_form_dto import CanalFormDTO
from src.application.dto.canal_list_dto import CanalListDTO
from src.application.dto.canal_list_item_dto import CanalListItemDTO
from src.domain.entities.canal_entity import CanalEntity
from src.domain.ports.outbound.canal_oficina_repository import CanalOficinaRepository
from src.domain.ports.outbound.canal_repository import CanalRepository


class GestionarCanalesUseCase:
    def __init__(
        self,
        canal_repo: CanalRepository,
        canal_oficina_repo: CanalOficinaRepository,
    ) -> None:
        self._canal_repo: CanalRepository = canal_repo
        self._canal_oficina_repo: CanalOficinaRepository = canal_oficina_repo

    async def listar_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        ind_activo: bool | None = None,
    ) -> CanalListDTO:
        entities, total = await self._canal_repo.listar_paginado_async(
            page=page,
            page_size=page_size,
            nombre=nombre,
            ind_activo=ind_activo,
        )
        items: list[CanalListItemDTO] = [
            CanalListItemDTO(
                cod_canales=entity.cod_canales or 0,
                nom_canales=entity.nom_canales,
                cpid=entity.cpid,
                cspid=entity.cspid,
                ind_activo=bool(entity.ind_activo),
                id_canales=entity.id_canales,
            )
            for entity in entities
        ]
        return CanalListDTO(items=items, total=total, page=page, page_size=page_size)

    async def listar_activas_async(self) -> list[CanalEntity]:
        return await self._canal_repo.listar_activas_async()

    async def obtener_async(self, cod_canales: int) -> CanalEntity | None:
        entity: CanalEntity | None = await self._canal_repo.obtener_por_id_async(cod_canales)
        if entity is None or entity.cod_canales is None:
            return entity
        entity.oficinas_ids = await self._canal_oficina_repo.listar_oficinas_por_canal_async(
            entity.cod_canales
        )
        return entity

    async def crear_async(self, dto: CanalFormDTO) -> CanalEntity:
        self._validar(dto)
        entity: CanalEntity = self._to_entity(dto)
        creado: CanalEntity = await self._canal_repo.crear_async(entity)
        if creado.cod_canales is not None:
            await self._canal_oficina_repo.reemplazar_oficinas_de_canal_async(
                creado.cod_canales, dto.oficinas_ids
            )
            creado.oficinas_ids = list(dto.oficinas_ids)
        return creado

    async def actualizar_async(
        self, cod_canales: int, dto: CanalFormDTO
    ) -> CanalEntity | None:
        self._validar(dto)
        entity: CanalEntity = self._to_entity(dto)
        actualizado: CanalEntity | None = await self._canal_repo.actualizar_async(
            cod_canales, entity
        )
        if actualizado is None:
            return None
        await self._canal_oficina_repo.reemplazar_oficinas_de_canal_async(
            cod_canales, dto.oficinas_ids
        )
        actualizado.oficinas_ids = list(dto.oficinas_ids)
        return actualizado

    @staticmethod
    def _validar(dto: CanalFormDTO) -> None:
        if not dto.nom_canales.strip():
            raise ValueError("nombre del canal es obligatorio")

    @staticmethod
    def _to_entity(dto: CanalFormDTO) -> CanalEntity:
        return CanalEntity(
            nom_canales=dto.nom_canales.strip(),
            cpid=dto.cpid,
            cspid=dto.cspid,
            ind_activo=dto.ind_activo,
            id_canales=dto.id_canales,
            oficinas_ids=list(dto.oficinas_ids),
        )
