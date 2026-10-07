from __future__ import annotations

import time
from collections.abc import Callable

from src.domain.exceptions.secreto_no_disponible import SecretoNoDisponible


class ProveedorSecretosPam:
    """AP-0062: adaptador al proveedor de credenciales de aplicacion de la herramienta PAM
    corporativa (p. ej. CyberArk CCP o AAM, Conjur, o un Key Vault rotado por PAM). Implementa
    ProveedorSecretos (PEP 544).

    El cliente concreto del proveedor corporativo se inyecta como `recuperador` (Callable), de
    modo que el adaptador es agnostico de la herramienta. No persiste el texto plano en disco;
    cachea en memoria con TTL para tolerar rotacion e invalida bajo demanda. Fail-secure: si el
    recuperador falla, lanza SecretoNoDisponible en vez de caer a un valor local.
    """

    def __init__(
        self,
        recuperador: Callable[[str], str],
        ttl_seg: int,
        reloj: Callable[[], float] = time.monotonic,
    ) -> None:
        self._recuperador: Callable[[str], str] = recuperador
        self._ttl_seg: int = ttl_seg
        self._reloj: Callable[[], float] = reloj
        self._cache: dict[str, tuple[float, str]] = {}

    def obtener(self, nombre: str) -> str | None:
        entrada: tuple[float, str] | None = self._cache.get(nombre)
        if entrada is not None and (self._reloj() - entrada[0]) < self._ttl_seg:
            return entrada[1] or None
        try:
            valor: str = self._recuperador(nombre)
        except Exception as exc:  # noqa: BLE001 -- fail-secure: no caer a valor local
            raise SecretoNoDisponible(
                f"AP-0062: el proveedor PAM no entrego el secreto '{nombre}'"
            ) from exc
        self._cache[nombre] = (self._reloj(), valor)
        return valor or None

    def invalidar(self, nombre: str) -> None:
        self._cache.pop(nombre, None)
