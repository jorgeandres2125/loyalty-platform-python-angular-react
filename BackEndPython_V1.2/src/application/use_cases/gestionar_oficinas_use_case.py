from __future__ import annotations

from src.application.dto.oficina_form_dto import OficinaFormDTO
from src.application.dto.oficina_list_dto import OficinaListDTO
from src.application.dto.oficina_list_item_dto import OficinaListItemDTO
from src.domain.entities.oficina_entity import OficinaEntity
from src.domain.ports.outbound.canal_oficina_repository import CanalOficinaRepository
from src.domain.ports.outbound.oficina_repository import OficinaRepository


class GestionarOficinasUseCase:
    def __init__(
        self,
        oficina_repo: OficinaRepository,
        canal_oficina_repo: CanalOficinaRepository,
    ) -> None:
        self._oficina_repo: OficinaRepository = oficina_repo
        self._canal_oficina_repo: CanalOficinaRepository = canal_oficina_repo

    async def listar_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        marca: str | None = None,
        regional: str | None = None,
        ind_activo: bool | None = None,
    ) -> OficinaListDTO:
        entities, total = await self._oficina_repo.listar_paginado_async(
            page=page,
            page_size=page_size,
            nombre=nombre,
            marca=marca,
            regional=regional,
            ind_activo=ind_activo,
        )
        items: list[OficinaListItemDTO] = [
            OficinaListItemDTO(
                cod_oficinas=entity.cod_oficinas or 0,
                id_oficinas=entity.id_oficinas,
                nom_oficinas=entity.nom_oficinas,
                marca=entity.marca,
                regional=entity.regional,
                cpid=entity.cpid,
                ind_activo=bool(entity.ind_activo),
                ciudad_nombre=entity.ciudad_nombre,
                did=entity.did,
                departamento_nombre=entity.departamento_nombre,
            )
            for entity in entities
        ]
        return OficinaListDTO(items=items, total=total, page=page, page_size=page_size)

    async def listar_activas_async(self) -> list[OficinaEntity]:
        return await self._oficina_repo.listar_activas_async()

    async def obtener_async(self, cod_oficinas: int) -> OficinaEntity | None:
        entity: OficinaEntity | None = await self._oficina_repo.obtener_por_id_async(cod_oficinas)
        if entity is None or entity.cod_oficinas is None:
            return entity
        entity.canales_ids = await self._canal_oficina_repo.listar_canales_por_oficina_async(
            entity.cod_oficinas
        )
        return entity

    async def crear_async(self, dto: OficinaFormDTO) -> OficinaEntity:
        self._validar(dto)
        entity: OficinaEntity = self._to_entity(dto)
        creado: OficinaEntity = await self._oficina_repo.crear_async(entity)
        if creado.cod_oficinas is not None:
            await self._canal_oficina_repo.reemplazar_canales_de_oficina_async(
                creado.cod_oficinas, dto.canales_ids
            )
            creado.canales_ids = list(dto.canales_ids)
        return creado

    async def actualizar_async(
        self, cod_oficinas: int, dto: OficinaFormDTO
    ) -> OficinaEntity | None:
        self._validar(dto)
        entity: OficinaEntity = self._to_entity(dto)
        actualizado: OficinaEntity | None = await self._oficina_repo.actualizar_async(
            cod_oficinas, entity
        )
        if actualizado is None:
            return None
        await self._canal_oficina_repo.reemplazar_canales_de_oficina_async(
            cod_oficinas, dto.canales_ids
        )
        actualizado.canales_ids = list(dto.canales_ids)
        return actualizado

    @staticmethod
    def _validar(dto: OficinaFormDTO) -> None:
        if not dto.nom_oficinas.strip():
            raise ValueError("nombre de la oficina es obligatorio")

    @staticmethod
    def _to_entity(dto: OficinaFormDTO) -> OficinaEntity:
        return OficinaEntity(
            id_oficinas=dto.id_oficinas,  # None en crear; el repo asigna MAX+1
            nom_oficinas=dto.nom_oficinas.strip(),
            marca=dto.marca.strip(),
            regional=dto.regional.strip(),
            cpid=dto.cpid,
            ind_activo=dto.ind_activo,
            canales_ids=list(dto.canales_ids),
        )
