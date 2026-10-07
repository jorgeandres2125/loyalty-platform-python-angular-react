"""AP-0087: el filtro redacta informacion sensible de los logs."""
from __future__ import annotations

import logging

from src.infrastructure.logging.redaccion_sensible_filter import RedaccionSensibleFilter


def _record(mensaje: str) -> logging.LogRecord:
    return logging.LogRecord("t", logging.INFO, __file__, 1, mensaje, None, None)


def test_redacta_password_en_mensaje() -> None:
    flt: RedaccionSensibleFilter = RedaccionSensibleFilter()
    rec: logging.LogRecord = _record("login fallido password=Secreta123 user=juan")
    flt.filter(rec)
    texto: str = rec.getMessage()
    assert "Secreta123" not in texto
    assert "[REDACTED]" in texto
    assert "user=juan" in texto


def test_redacta_jwt() -> None:
    flt: RedaccionSensibleFilter = RedaccionSensibleFilter()
    jwt: str = "eyJhbGciOiJI.eyJzdWIiOiI1.abcDEF123"
    rec: logging.LogRecord = _record("token emitido " + jwt)
    flt.filter(rec)
    assert jwt not in rec.getMessage()


def test_redacta_bearer() -> None:
    flt: RedaccionSensibleFilter = RedaccionSensibleFilter()
    rec: logging.LogRecord = _record("Authorization: Bearer abc.def.ghi")
    flt.filter(rec)
    assert "abc.def.ghi" not in rec.getMessage()


def test_redacta_extra_por_clave() -> None:
    flt: RedaccionSensibleFilter = RedaccionSensibleFilter()
    rec: logging.LogRecord = _record("evento")
    setattr(rec, "password", "Secreta123")
    setattr(rec, "usuario", "juan")
    flt.filter(rec)
    assert getattr(rec, "password") == "[REDACTED]"
    assert getattr(rec, "usuario") == "juan"


def test_redacta_extra_dict_anidado() -> None:
    flt: RedaccionSensibleFilter = RedaccionSensibleFilter()
    rec: logging.LogRecord = _record("evento")
    setattr(rec, "datos", {"token": "xyz", "nombre": "Juan"})
    flt.filter(rec)
    datos: dict[str, object] = getattr(rec, "datos")
    assert datos["token"] == "[REDACTED]"
    assert datos["nombre"] == "Juan"


def test_mensaje_sin_sensibles_intacto() -> None:
    flt: RedaccionSensibleFilter = RedaccionSensibleFilter()
    rec: logging.LogRecord = _record("usuario juan inicio sesion correctamente")
    flt.filter(rec)
    assert rec.getMessage() == "usuario juan inicio sesion correctamente"
