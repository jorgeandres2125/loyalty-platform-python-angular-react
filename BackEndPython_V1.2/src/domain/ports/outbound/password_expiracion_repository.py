from __future__ import annotations

from datetime import datetime
from typing import Protocol


class PasswordExpiracionRepository(Protocol):
    """AP-0037: puerto de salida del reloj de vencimiento de contrasena (PEP 544).

    Persiste, por usuario, el instante del ultimo cambio de contrasena
    (password_cambiado_en), base de calculo del vencimiento. No toca dbo.users
    (propiedad de Drupal); vive en la tabla lateral user_password_expiracion.
    Un adaptador satisface el contrato por forma, sin heredar.
    """

    async def obtener_cambiado_en(self, uid: int) -> datetime | None: ...

    async def registrar_cambio(self, uid: int, cuando: datetime) -> None: ...

    async def asegurar_baseline(self, uid: int, cuando: datetime) -> None: ...
