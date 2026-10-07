from __future__ import annotations

from typing import Protocol


class SondaPermisosObjeto(Protocol):
    """AP-0061: puerto de sondeo de anomalias de minimo privilegio sobre objetos de BD.

    A diferencia de AP-0056 (que sondea la membresia de rol del principal), este puerto
    detecta permisos excesivos heredados hacia objetos nuevos: EXECUTE a nivel de base de
    datos sobre la cuenta de la app, y cualquier GRANT sobre objetos de usuario al principal
    publico. Devuelve la lista de anomalias en texto legible; vacia si el estado es de
    minimo privilegio.
    """

    async def anomalias_minimo_privilegio(self) -> list[str]: ...
