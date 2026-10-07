from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.shared.constants.rate_limit_policy import (
    RATE_LIMIT_POR_IP_AUTH,
    RATE_LIMIT_POR_IP_DEFECTO,
)

# AP-0166: limites efectivos por IP. Se leen en cada peticion mediante los
# proveedores dinamicos de abajo. slowapi 0.1.10 invoca el proveedor de limite
# SIN argumentos (slowapi/wrappers.py -> Limit.__iter__ -> self.__limit_provider());
# por eso deben ser callables de cero argumentos. Un parametro request provoca
# "missing 1 required positional argument". La configurabilidad por .env se logra
# mutando estas variables de modulo desde create_app (composition root).
_limite_auth_actual: str = RATE_LIMIT_POR_IP_AUTH
_limite_defecto_actual: str = RATE_LIMIT_POR_IP_DEFECTO


def _limite_auth() -> str:
    return _limite_auth_actual


def _limite_defecto() -> str:
    return _limite_defecto_actual


def configurar_limites(limite_auth: str, limite_defecto: str) -> None:
    """Fija los limites por IP desde Settings (.env). Llamar solo en create_app."""
    global _limite_auth_actual, _limite_defecto_actual
    _limite_auth_actual = limite_auth
    _limite_defecto_actual = limite_defecto


# AP-0166: instancia unica del limitador. El limite por defecto (proveedor de cero
# argumentos) lo aplica SlowAPIMiddleware a toda ruta sin limite propio; el login
# define su propio limite mas estricto via decorador, que tiene prioridad.
limiter: Limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[_limite_defecto],
)
