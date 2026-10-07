from __future__ import annotations

import logging

from src.application.dto.token_sapin_request_dto import TokenSAPINRequestDTO
from src.application.dto.token_sapin_response_dto import TokenSAPINResponseDTO
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.ports.outbound.perfil_repository import PerfilRepository
from src.domain.services.cifrador_sapin_versionado import CifradorSapinVersionado

logger: logging.Logger = logging.getLogger(__name__)


class GenerarTokenSAPINUseCase:
    def __init__(
        self,
        cifrador: CifradorSapinVersionado,
        perfil_repo: PerfilRepository,
        url_sapin: str = "",
    ) -> None:
        self._cifrador: CifradorSapinVersionado = cifrador
        self._perfil_repo: PerfilRepository = perfil_repo
        self._url_sapin: str = url_sapin

    async def ejecutar_async(self, dto: TokenSAPINRequestDTO) -> TokenSAPINResponseDTO:
        perfil: PerfilContactoEntity | None = await self._perfil_repo.obtener_contacto_async(
            dto.cedula
        )
        nombre: str = perfil.nombre_completo if perfil else ""
        token = self._cifrador.generar_token(dto.cedula, nombre, dto.alianza)
        logger.info("sapin_token_generado", extra={"cedula": dto.cedula})
        return TokenSAPINResponseDTO(
            token=token.token_cifrado,
            cedula=dto.cedula,
            url_sapin=self._url_sapin,
        )
