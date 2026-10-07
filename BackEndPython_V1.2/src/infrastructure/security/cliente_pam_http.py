from __future__ import annotations

from collections.abc import Callable

from src.domain.exceptions.secreto_no_disponible import SecretoNoDisponible


class ClientePamHttp:
    """AP-0062: cliente del proveedor de credenciales de aplicacion de la herramienta PAM
    corporativa, sobre HTTP. Es agnostico de la herramienta concreta mediante configuracion:

    - base_url: la URL del servicio (incluye la ruta), inyectada por Infra por entorno.
    - app_id y safe: identifican la aplicacion y el contenedor de secretos (convencion de
      CyberArk CCP o AAM; en Conjur o Key Vault quedan vacios y se omiten).
    - campo_secreto: ruta con puntos del campo del JSON que contiene el secreto
      (p. ej. 'Content' en CyberArk CCP, o 'data.data.password' en Vault KV v2).

    La llamada HTTP se inyecta como `http_get` (Callable), de modo que la logica de armado de
    parametros y extraccion es pura y testeable. La cache con TTL y el fail-secure los aporta
    ProveedorSecretosPam, que envuelve a este cliente.
    """

    def __init__(
        self,
        base_url: str,
        app_id: str,
        safe: str,
        campo_secreto: str,
        http_get: Callable[[str, dict[str, str]], dict[str, object]],
    ) -> None:
        self._base_url: str = base_url
        self._app_id: str = app_id
        self._safe: str = safe
        self._campo_secreto: str = campo_secreto
        self._http_get: Callable[[str, dict[str, str]], dict[str, object]] = http_get

    def recuperar(self, nombre: str) -> str:
        parametros: dict[str, str] = {"AppID": self._app_id, "Safe": self._safe, "Object": nombre}
        consulta: dict[str, str] = {clave: valor for clave, valor in parametros.items() if valor}
        datos: dict[str, object] = self._http_get(self._base_url, consulta)
        valor: object | None = self._extraer(datos, self._campo_secreto)
        if not isinstance(valor, str) or not valor:
            raise SecretoNoDisponible(
                f"AP-0062: el proveedor PAM no devolvio el campo del secreto para '{nombre}'"
            )
        return valor

    @staticmethod
    def _extraer(datos: dict[str, object], ruta: str) -> object | None:
        actual: object | None = datos
        for parte in ruta.split("."):
            if not isinstance(actual, dict):
                return None
            actual = actual.get(parte)
        return actual
