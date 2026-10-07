from __future__ import annotations


class PermisoObjetoExcesivo(Exception):
    """AP-0061: la cuenta de BD conectada por la app hereda permisos excesivos sobre objetos
    (p. ej. EXECUTE a nivel de base de datos, que alcanza a todo procedimiento o funcion
    actual y futuro), violando el minimo privilegio de objetos nuevos. En staging y
    produccion aborta el arranque (fail-fast).
    """
