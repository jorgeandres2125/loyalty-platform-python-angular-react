from __future__ import annotations

from typing import Protocol

from src.domain.value_objects.codigo_verificacion import CodigoVerificacion


class CodigoVerificacionStore(Protocol):
    """Almacén con expiración (TTL) para los códigos OTP de verificación (AP-0004).

    Contrato estructural (PEP 544): el adaptador por defecto es en memoria, pero un
    Redis/SQL puede sustituirlo sin cambiar la firma. El TTL lo aplica el adaptador.
    """

    async def guardar(self, clave: str, registro: CodigoVerificacion) -> None: ...
    async def obtener(self, clave: str) -> CodigoVerificacion | None: ...
    async def eliminar(self, clave: str) -> None: ...
