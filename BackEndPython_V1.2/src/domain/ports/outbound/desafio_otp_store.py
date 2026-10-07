from __future__ import annotations

from typing import Protocol

from src.domain.entities.desafio_otp_login import DesafioOtpLogin


class DesafioOtpStore(Protocol):
    """AP-0012: almacen con expiracion (TTL) de los desafios OTP de login.

    Contrato estructural (PEP 544). El adaptador por defecto es en memoria; un Redis o
    SQL puede sustituirlo sin cambiar la firma. El TTL lo aplica el adaptador: `obtener`
    devuelve None si el desafio ya expiro.
    """

    async def guardar(self, desafio_id: str, desafio: DesafioOtpLogin) -> None: ...
    async def obtener(self, desafio_id: str) -> DesafioOtpLogin | None: ...
    async def eliminar(self, desafio_id: str) -> None: ...
