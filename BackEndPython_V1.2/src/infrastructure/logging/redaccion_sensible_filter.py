from __future__ import annotations

import logging
import re
from typing import Final

from src.shared.constants.redaccion_logs import CLAVES_SENSIBLES, REDACTADO

_CLAVES_REGEX: Final[str] = (
    "password|contrasena|pwd|passwd|secret|token|authorization|"
    "api[_-]?key|apikey|jwt|otp|csrf|cookie"
)
_RE_KV: Final[re.Pattern[str]] = re.compile(
    r"(?i)\b(" + _CLAVES_REGEX + r")\b(\s{0,4}[=:]\s{0,4})([^\s,;&}]+)"
)
_RE_JWT: Final[re.Pattern[str]] = re.compile(
    r"eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{2,}"
)
_RE_BEARER: Final[re.Pattern[str]] = re.compile(r"(?i)\bbearer\s{1,4}[A-Za-z0-9._-]+")

_RESERVADOS: Final[frozenset[str]] = frozenset(
    {
        "name", "msg", "args", "levelname", "levelno", "pathname",
        "filename", "module", "exc_info", "exc_text", "stack_info",
        "lineno", "funcName", "created", "msecs", "relativeCreated",
        "thread", "threadName", "processName", "process", "message",
        "taskName",
    }
)


class RedaccionSensibleFilter(logging.Filter):
    """AP-0087: redacta informacion sensible de los LogRecord antes de emitirlos.

    Se adjunta al handler raiz para cubrir todos los loggers (incluidos los hijos
    como 'sufi.seguridad'). Redacta: (1) el mensaje formateado por patrones (JWT,
    Bearer, clave=valor sensible) y (2) los campos extra cuya clave sea sensible,
    recursivamente en dicts y listas. No toca el identificador de usuario ni la IP,
    necesarios para la trazabilidad de auditoria.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        mensaje: str = record.getMessage()
        redactado: str = self._redactar_texto(mensaje)
        if redactado != mensaje:
            record.msg = redactado
            record.args = ()
        for clave in list(record.__dict__.keys()):
            if clave in _RESERVADOS:
                continue
            if clave.lower() in CLAVES_SENSIBLES:
                record.__dict__[clave] = REDACTADO
            else:
                record.__dict__[clave] = self._redactar_valor(record.__dict__[clave])
        return True

    def _redactar_texto(self, texto: str) -> str:
        resultado: str = _RE_JWT.sub(REDACTADO, texto)
        resultado = _RE_BEARER.sub("Bearer " + REDACTADO, resultado)
        resultado = _RE_KV.sub(self._reemplazar_kv, resultado)
        return resultado

    @staticmethod
    def _reemplazar_kv(coincidencia: re.Match[str]) -> str:
        return coincidencia.group(1) + coincidencia.group(2) + REDACTADO

    def _redactar_valor(self, valor: object) -> object:
        if isinstance(valor, str):
            return self._redactar_texto(valor)
        if isinstance(valor, dict):
            return {
                clave: (
                    REDACTADO
                    if isinstance(clave, str) and clave.lower() in CLAVES_SENSIBLES
                    else self._redactar_valor(val)
                )
                for clave, val in valor.items()
            }
        if isinstance(valor, (list, tuple)):
            return [self._redactar_valor(elem) for elem in valor]
        return valor
