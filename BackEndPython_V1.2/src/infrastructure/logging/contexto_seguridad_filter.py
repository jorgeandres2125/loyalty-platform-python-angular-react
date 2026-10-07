from __future__ import annotations

import logging

from src.infrastructure.logging.contexto_seguridad import ContextoSeguridad


class ContextoSeguridadFilter(logging.Filter):
    """Inyecta el contexto de correlación (AP-0024) en cada LogRecord.

    Añade evento_id, usuario, ip_publica, ip_local, metodo y ruta a todo registro
    emitido dentro de una petición, sin sobrescribir atributos ya presentes. Así
    cualquier log (de seguridad o excepcional) queda correlacionado con su petición.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        for clave, valor in ContextoSeguridad.actual().items():
            if not hasattr(record, clave):
                setattr(record, clave, valor)
        return True
