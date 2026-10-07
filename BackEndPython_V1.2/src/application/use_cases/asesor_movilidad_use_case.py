from __future__ import annotations

import math
from datetime import date

from src.domain.entities.comisionista_programa_entity import ComisionistaProgramaEntity
from src.domain.entities.comisionista_subprograma_entity import ComisionistaSubprogramaEntity
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.entities.perfil_emocional_entity import PerfilEmocionalEntity
from src.domain.entities.perfil_tributario_entity import PerfilTributarioEntity
from src.domain.exceptions.email_no_unico import EmailNoUnico
from src.domain.exceptions.paso_omitido import PasoOmitido
from src.domain.ports.outbound.asesor_movilidad_repository import AsesorMovilidadRepository
from src.domain.ports.outbound.perfil_repository import PerfilRepository
from src.domain.value_objects.email import Email


class AsesorMovilidadUseCase:
    """Casos de uso para Asesores de Movilidad (users_perfil_contacto, cpid=1)."""

    def __init__(
        self,
        asesor_repo: AsesorMovilidadRepository,
        perfil_repo: PerfilRepository,
    ) -> None:
        self._asesor_repo: AsesorMovilidadRepository = asesor_repo
        self._perfil_repo: PerfilRepository = perfil_repo

    async def listar_async(self, page: int, size: int, tipo_doc: str | None = None, documento: str | None = None) -> dict:
        items, total = await self._asesor_repo.listar_async(page, size, tipo_doc=tipo_doc, documento=documento)
        pages: int = math.ceil(total / size) if size > 0 else 0
        return {"items": items, "total": total, "page": page, "size": size, "pages": pages}

    async def obtener_detalle_async(self, numero_documento: str) -> dict:
        contacto: PerfilContactoEntity | None = await self._perfil_repo.obtener_contacto_async(numero_documento)
        tributario: PerfilTributarioEntity | None = await self._perfil_repo.obtener_tributario_async(numero_documento)
        emocional: PerfilEmocionalEntity | None = await self._perfil_repo.obtener_emocional_async(numero_documento)
        return {"contacto": contacto, "tributario": tributario, "emocional": emocional}

    async def listar_subprogramas_async(self, cpid: int) -> list[ComisionistaSubprogramaEntity]:
        return await self._perfil_repo.listar_subprogramas_async()

    async def guardar_paso1_async(self, entity: PerfilContactoEntity) -> PerfilContactoEntity:
        if entity.email:
            correo: str = Email(entity.email).valor
            entity.email = correo
            existente: str | None = await self._perfil_repo.numero_documento_por_email_async(correo)
            if existente is not None and existente != entity.numero_documento:
                raise EmailNoUnico(correo, existente)
        return await self._perfil_repo.guardar_contacto_async(entity)

    async def guardar_paso2_async(self, entity: PerfilTributarioEntity) -> PerfilTributarioEntity:
        # AP-0187: el paso 2 exige que el paso 1 (contacto) ya exista en el servidor.
        if await self._perfil_repo.obtener_contacto_async(entity.numero_documento) is None:
            raise PasoOmitido("Debe completar el paso 1 (datos de contacto) antes del paso 2.")
        entity.estado = 0
        entity.fecha_alta = date.today()
        return await self._perfil_repo.guardar_tributario_async(entity)

    async def guardar_paso3_async(self, entity: PerfilEmocionalEntity) -> PerfilEmocionalEntity:
        # AP-0187: el paso 3 exige los pasos 1 (contacto) y 2 (tributario).
        nd: str = entity.numero_documento
        if await self._perfil_repo.obtener_contacto_async(nd) is None:
            raise PasoOmitido("Debe completar el paso 1 (datos de contacto) antes del paso 3.")
        if await self._perfil_repo.obtener_tributario_async(nd) is None:
            raise PasoOmitido("Debe completar el paso 2 (datos tributarios) antes del paso 3.")
        return await self._perfil_repo.guardar_emocional_async(entity)

    async def finalizar_async(self, numero_documento: str) -> PerfilContactoEntity:
        # AP-0187: finalizar exige los tres pasos completados; ninguno puede saltarse.
        contacto: PerfilContactoEntity | None = await self._perfil_repo.obtener_contacto_async(numero_documento)
        if contacto is None:
            raise PasoOmitido("Debe completar el paso 1 (datos de contacto) antes de finalizar.")
        if await self._perfil_repo.obtener_tributario_async(numero_documento) is None:
            raise PasoOmitido("Debe completar el paso 2 (datos tributarios) antes de finalizar.")
        if await self._perfil_repo.obtener_emocional_async(numero_documento) is None:
            raise PasoOmitido("Debe completar el paso 3 (perfil emocional) antes de finalizar.")
        contacto.fecha_completado = date.today()
        return await self._perfil_repo.guardar_contacto_async(contacto)

    async def verificar_async(self, numero_documento: str) -> dict:
        contacto: PerfilContactoEntity | None = await self._perfil_repo.obtener_contacto_async(numero_documento)
        if contacto:
            return {"registrado": True, "estado": contacto.estado}
        return {"registrado": False, "estado": None}

    async def listar_programas_async(self) -> list[ComisionistaProgramaEntity]:
        return await self._perfil_repo.listar_programas_async()
