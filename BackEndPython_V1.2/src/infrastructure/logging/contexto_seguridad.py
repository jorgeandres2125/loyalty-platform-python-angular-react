from __future__ import annotations

from contextvars import ContextVar, Token

_CONTEXTO: ContextVar[dict[str, object]] = ContextVar("contexto_seguridad", default={})


class ContextoSeguridad:
    """Contexto de correlación por petición para los logs (AP-0024).

    Guarda en un `ContextVar` el envoltorio {evento_id, usuario, ip_publica,
    ip_local, metodo, ruta} que un filtro de logging inyecta en cada registro, de
    modo que todo evento (de seguridad o excepcional) sea investigable/correlacionable.
    El valor se fija por petición en un middleware ASGI y se limpia al terminar.
    """

    @staticmethod
    def establecer(datos: dict[str, object]) -> Token[dict[str, object]]:
        return _CONTEXTO.set(datos)

    @staticmethod
    def limpiar(token: Token[dict[str, object]]) -> None:
        _CONTEXTO.reset(token)

    @staticmethod
    def actual() -> dict[str, object]:
        return _CONTEXTO.get()
