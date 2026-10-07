from __future__ import annotations


class AccesoNoAutorizado(Exception):
    """AP-0053: el actor intento operar sobre un recurso que no le pertenece
    (escalamiento horizontal / IDOR). Se traduce a 403 en el borde HTTP."""
