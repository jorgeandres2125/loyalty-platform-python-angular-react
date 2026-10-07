import json
import logging
import traceback
from datetime import UTC, datetime

from src.domain.services.clasificador_retencion import ClasificadorRetencion
from src.domain.value_objects.retencion_categoria import RetencionCategoria
from src.infrastructure.logging.contexto_seguridad_filter import ContextoSeguridadFilter
from src.infrastructure.logging.redaccion_sensible_filter import RedaccionSensibleFilter
from src.infrastructure.logging.retencion_log_filter import RetencionLogFilter
from src.infrastructure.logging.sellador_log_filter import SelladorLogFilter
from src.infrastructure.security.sellador_cadena_en_memoria import SelladorCadenaEnMemoria


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
        }
        if record.exc_info:
            entry["exception"] = traceback.format_exception(*record.exc_info)
        extra_skip = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "message",
            "taskName",
        }
        extra = {k: v for k, v in record.__dict__.items() if k not in extra_skip}
        if extra:
            entry["extra"] = extra
        return json.dumps(entry, ensure_ascii=False, default=str)


def configurar_logging(
    level: str = "INFO",
    formato: str = "json",
    sellado_enabled: bool = True,
    retencion_dias: dict[RetencionCategoria, int] | None = None,
) -> None:
    handler = logging.StreamHandler()
    if formato == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s — %(message)s"))
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()
    handler.addFilter(RedaccionSensibleFilter())
    # AP-0026: clasifica cada log con su categoria y plazo de retencion para el
    # enrutado y el ciclo de vida en el destino centralizado.
    if retencion_dias is not None:
        handler.addFilter(RetencionLogFilter(ClasificadorRetencion(retencion_dias)))
    # AP-0025: sella cada evento de seguridad con un eslabon de hash encadenado
    # (tamper-evidence) despues de redactar; el sello viaja al destino inmutable.
    if sellado_enabled:
        handler.addFilter(SelladorLogFilter(SelladorCadenaEnMemoria()))
    root.addHandler(handler)
    root.addFilter(ContextoSeguridadFilter())
    # Silencia librerías ruidosas
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
