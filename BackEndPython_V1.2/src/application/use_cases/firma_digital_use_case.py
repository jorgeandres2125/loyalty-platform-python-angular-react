from __future__ import annotations

import base64
import binascii
import hashlib
import json
import logging
import secrets
from datetime import UTC, datetime

from src.application.dto.resultado_firma_dto import ResultadoFirmaDTO
from src.application.dto.resultado_verificacion_firma_dto import ResultadoVerificacionFirmaDTO
from src.domain.entities.evidencia_firma import EvidenciaFirma
from src.domain.ports.outbound.evidencia_firma_store import EvidenciaFirmaStore
from src.domain.ports.outbound.firmador_digital import FirmadorDigital
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD
from src.shared.constants.firma import EVENTO_FIRMA, HASH_GENESIS

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


class FirmaDigitalUseCase:
    """AP-0006: firma y verificacion de informacion y transacciones sensibles.

    `firmar_async` canonicaliza el payload, calcula su hash SHA-256, lo firma con la
    clave asimetrica (ES256) via el puerto FirmadorDigital y persiste una EvidenciaFirma
    encadenada por hash (tamper-evident). `verificar_async` reconstruye el canonico y
    valida la firma. Cada operacion se audita en el logger de seguridad (AP-0022).
    """

    def __init__(
        self, firmador: FirmadorDigital, evidencia_store: EvidenciaFirmaStore
    ) -> None:
        self._firmador: FirmadorDigital = firmador
        self._evidencia_store: EvidenciaFirmaStore = evidencia_store

    async def firmar_async(
        self, recurso_tipo: str, recurso_id: str, payload: dict[str, object], emisor: str
    ) -> ResultadoFirmaDTO:
        canonico: bytes = self._canonicalizar(payload)
        hash_payload: str = hashlib.sha256(canonico).hexdigest()
        firma: bytes = self._firmador.firmar(canonico)
        valor_firma: str = base64.urlsafe_b64encode(firma).decode("ascii")
        anterior: EvidenciaFirma | None = await self._evidencia_store.ultimo()
        hash_anterior: str = (
            anterior.hash_evidencia if anterior is not None else HASH_GENESIS
        )
        evidencia_id: str = secrets.token_urlsafe(16)
        creado: str = datetime.now(UTC).isoformat()
        hash_evidencia: str = self._hash_encadenado(
            evidencia_id,
            recurso_tipo,
            recurso_id,
            hash_payload,
            valor_firma,
            emisor,
            creado,
            hash_anterior,
        )
        evidencia: EvidenciaFirma = EvidenciaFirma(
            id=evidencia_id,
            recurso_tipo=recurso_tipo,
            recurso_id=recurso_id,
            alg=self._firmador.algoritmo,
            kid=self._firmador.kid,
            hash_payload=hash_payload,
            valor_firma=valor_firma,
            emisor=emisor,
            creado_en_iso=creado,
            hash_anterior=hash_anterior,
            hash_evidencia=hash_evidencia,
        )
        await self._evidencia_store.guardar(evidencia)
        _logger.info(
            "firma emitida recurso=%s emisor=%s kid=%s",
            recurso_tipo,
            emisor,
            self._firmador.kid,
            extra=self._campos("exito", emisor, recurso_tipo),
        )
        return ResultadoFirmaDTO(
            evidencia_id=evidencia_id,
            kid=self._firmador.kid,
            alg=self._firmador.algoritmo.value,
            valor_firma=valor_firma,
            hash_payload=hash_payload,
            hash_evidencia=hash_evidencia,
        )

    async def verificar_async(
        self, payload: dict[str, object], valor_firma: str
    ) -> ResultadoVerificacionFirmaDTO:
        canonico: bytes = self._canonicalizar(payload)
        try:
            firma: bytes = base64.urlsafe_b64decode(self._pad(valor_firma))
        except (binascii.Error, ValueError):
            return ResultadoVerificacionFirmaDTO(
                valida=False, kid=self._firmador.kid, alg=self._firmador.algoritmo.value
            )
        valida: bool = self._firmador.verificar(canonico, firma)
        _logger.info(
            "firma verificada valida=%s kid=%s",
            valida,
            self._firmador.kid,
            extra=self._campos("exito" if valida else "fallo", "verificador", "verificacion"),
        )
        return ResultadoVerificacionFirmaDTO(
            valida=valida, kid=self._firmador.kid, alg=self._firmador.algoritmo.value
        )

    # -- Helpers --
    @staticmethod
    def _campos(resultado: str, actor: str, recurso: str) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_FIRMA,
            "resultado": resultado,
            "actor": actor,
            "recurso": recurso,
        }

    @staticmethod
    def _canonicalizar(payload: dict[str, object]) -> bytes:
        return json.dumps(
            payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")

    @staticmethod
    def _pad(valor: str) -> str:
        faltan: int = (-len(valor)) % 4
        return valor + ("=" * faltan)

    @staticmethod
    def _hash_encadenado(*partes: str) -> str:
        cadena: str = chr(31).join(partes)
        return hashlib.sha256(cadena.encode("utf-8")).hexdigest()
