from __future__ import annotations

from typing import Protocol


class ProveedorSecretos(Protocol):
    """AP-0062: puerto de salida para obtener secretos de la aplicacion (credenciales de BD,
    de integracion, claves) desde el origen custodiado.

    En dev y test lo implementa un proveedor de entorno; en staging y produccion, un adaptador
    a la herramienta PAM corporativa (proveedor de credenciales de aplicacion), que permite
    rotacion sin redeploy. `invalidar` fuerza el re-fetch tras una rotacion o un fallo de auth.
    """

    def obtener(self, nombre: str) -> str | None: ...

    def invalidar(self, nombre: str) -> None: ...
