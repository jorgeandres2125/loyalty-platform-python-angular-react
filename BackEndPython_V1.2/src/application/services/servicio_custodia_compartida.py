from __future__ import annotations

import base64
import binascii
import logging

from src.domain.exceptions.custodia_insuficiente import CustodiaInsuficiente
from src.domain.ports.outbound.custodia_compartida_clave import CustodiaCompartidaClave
from src.shared.constants.custodia import EVENTO_CUSTODIA
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


class ServicioCustodiaCompartida:
    """AP-0015: doble custodia de la KEK maestra por reparto de Shamir.

    Reconstruye la KEK a partir de los shares que inyectan custodios independientes
    (ninguno solo la posee), exigiendo el umbral configurado (fail-closed): con menos de
    `umbral` shares lanza CustodiaInsuficiente y el sistema no arranca. Tambien puede
    dividir una KEK en shares para la ceremonia de alta. Cada reconstruccion se audita en
    el logger de seguridad (AP-0022).
    """

    def __init__(self, reparto: CustodiaCompartidaClave, umbral: int) -> None:
        self._reparto: CustodiaCompartidaClave = reparto
        self._umbral: int = umbral

    def dividir_kek(self, kek: bytes, total: int) -> list[str]:
        shares: list[bytes] = self._reparto.dividir(kek, total, self._umbral)
        return [base64.b64encode(share).decode("ascii") for share in shares]

    def reconstruir_kek(self, shares_b64: list[str]) -> bytes:
        presentes: list[str] = [share for share in shares_b64 if share.strip()]
        if len(presentes) < self._umbral:
            _logger.error(
                "AP-0015 doble custodia insuficiente (%d shares, se requieren %d)",
                len(presentes),
                self._umbral,
                extra=self._campos("fallo"),
            )
            raise CustodiaInsuficiente(
                "doble custodia (se requieren "
                + str(self._umbral)
                + " shares, hay "
                + str(len(presentes))
                + ")"
            )
        try:
            shares: list[bytes] = [base64.b64decode(share) for share in presentes]
        except (binascii.Error, ValueError) as exc:
            raise CustodiaInsuficiente("share de custodia con base64 invalido") from exc
        kek: bytes = self._reparto.reconstruir(shares)
        _logger.info(
            "AP-0015 KEK reconstruida por doble custodia con %d shares",
            len(shares),
            extra=self._campos("exito"),
        )
        return kek

    @staticmethod
    def _campos(resultado: str) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_CUSTODIA,
            "resultado": resultado,
            "actor": "custodia",
        }
